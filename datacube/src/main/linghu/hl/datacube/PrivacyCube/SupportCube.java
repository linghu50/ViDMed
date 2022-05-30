package main.linghu.hl.datacube.PrivacyCube;

import main.linghu.hl.datacube.api.IQueryEngine;
import main.linghu.hl.datacube.api.tree.IContent;
import main.linghu.hl.datacube.api.utils.tuples.Tuple2;
import org.apache.commons.math3.ml.distance.DistanceMeasure;

import java.util.*;
import java.util.stream.Collectors;

public class SupportCube {
    public final PNode root;
    public final List<Tuple2<String, List<Object>>> schemaMap;
    public List<List<Integer>> cuboids = new ArrayList<>();

    public SupportCube() {
        this(new ArrayList<>());
    }

    public SupportCube(List<Tuple2<String, List<Object>>> schemaMap) {
        root = new PNode(Set.of(0));
        this.schemaMap = schemaMap;
    }
    // 从datacube中构造页面操作用的webtree
    public WebNode getWebTree(List<Integer> schema, List<Integer> sensitives, DistanceMeasure distanceMeasure) {
        Stack<WebNode> path = new Stack<>();
        WebNode child = new WebNode();
        child.labels.add(-1);
        path.push(child);
        List<List<Set<Integer>>> queries = new ArrayList<>();
        for (int i = 0; i < schemaMap.size(); i++) {
            queries.add(new ArrayList<>());
        }
        List<double[]> globals = new ArrayList<>();
        var content = query(queries);
        for (Integer sensitive : sensitives) {
            globals.add(content.getDistribute(sensitive, schemaMap.get(sensitive).y.size()));
        }
        return dfsWebTree(schema, path, sensitives, globals, distanceMeasure);
    }

    private WebNode dfsWebTree(List<Integer> schema, Stack<WebNode> path, List<Integer> sensitives, List<double[]> globals, DistanceMeasure distanceMeasure) {
        WebNode root = path.peek();
        List<List<Set<Integer>>> queries = new ArrayList<>();
        for (int i = 0; i < schemaMap.size(); i++) {
            boolean flag = true;
            for (int j = 0; j < schema.size(); j++) {
                if (schema.get(j) == i && path.size() - 1 > j) {
                    List<Set<Integer>> query = new ArrayList<>();
                    query.add(path.get(j + 1).labels);
                    queries.add(query);
                    flag = false;
                }
            }
            if (flag) {
                queries.add(new ArrayList<>());
            }
        }
        root.content = query(queries);
        if (root.content == null || root.content.inValid()) {
            return null;
        }

        root.content.update_k_Anonymous();
        root.content.update_l_Diversity(sensitives);
        root.content.update_t_closeness(sensitives, globals, distanceMeasure);


        root.count = root.content.d.size();
        if (schema.size() == path.size() - 1) {
            root.branch = 1;
            return root;
        }
//        int size = schemaMap.get(schema.get(path.size() - 1)).y.size();
//        for (int i = 0; i < size; i++) {
//            WebNode child = new WebNode();
//            child.labels.add((Integer) i);
//            path.push(child);
//            child = dfsWebTree(schema, path, sensitives, globals, distanceMeasure);
//            path.pop();
//            if (child != null) {
//                root.children.add(child);
//            }
//        }

        PNode node = this.root;
        for (int i = 0; i < schema.get(path.size() - 1); i++) {
            node = (PNode) node.content;
        }
        for (PNode childNode : node.getChildren()) {
            WebNode child = new WebNode();
            child.labels = childNode.getLabel();
            path.push(child);
            child = dfsWebTree(schema, path, sensitives, globals, distanceMeasure);
            path.pop();
            if (child != null) {
                root.children.add(child);
            }
        }

        root.children.forEach(child->{
            root.branch += child.branch;
        });
        return root;
    }

    public int getCount(PNode root) {
        IContent content = root.getContent();
        while (content instanceof PNode node) {
            content = node.getContent();
        }
        return ((TableCuboid)content).d.size();
    }

    public void insert(TabularDataPoint dataPoint) {
        add(root, dataPoint, 0, new HashSet<>());
    }

    public IQueryEngine getQueryEngine() {
        return null;
    }

    public void updateCuboid(List<List<Set<Integer>>> query) {
        List<Integer> cuboid = query.stream().map(List::size).collect(Collectors.toList());
        if (!cuboids.contains(cuboid)) {
            addCuboid(cuboid);
        }
    }

    public TableCuboid query(List<List<Set<Integer>>> query) {
        TableCuboid result = getCuboidInstance();
        queryDFS(root, result, query, 0);
        updateCuboid(query);
        return result;
    }

    private TableCuboid queryDFS(PNode rootNode, TableCuboid result, List<List<Set<Integer>>> query, int dimension) {
        if (dimension >= query.size())
            return result;
        List<Set<Integer>> chain = query.get(dimension);
        PNode node = rootNode;
        for (Set<Integer> aInteger : chain) {
            node = node.getChild(aInteger);
            if (node == null)
                return result;
        }
        return checkContentNull(result, node, dimension, query);
    }

    public void addCuboid(List<Integer> schema) {
        addCuboid(root, schema, cuboids.get(0));
        cuboids.add(schema);
    }
    private void addCuboid(PNode root, List<Integer> new_schema, List<Integer> basic_schema) {
        List<IContent> nodes = new ArrayList<>();
        List<List<IContent>> candidates = new ArrayList<>();
        nodes.add(root);
        candidates.add(new ArrayList<>());
        candidates.get(0).add(root);

        for(int i=0;i<new_schema.size()-1;i++) {
            var back = addCuboidChildren(nodes,candidates,0,new_schema.get(i));
            List<IContent> next_nodes = back.x;
            List<List<IContent>> next_candi = back.y;
            nodes.clear();
            candidates.clear();
            for(int k=0;k<next_nodes.size();k++) {
                PNode node = (PNode) next_nodes.get(k);
                List<IContent> candi = next_candi.get(k);
                Stack<IContent> children = new Stack<>();
                for(int j=0;j<candi.size();j++) {
                    int depth = basic_schema.get(i)-new_schema.get(i);
                    getChildrenRec(candi.get(j), depth, children);
                }
                if(node.getContent() == null) {
                    if(children.size() == 1)
                        node.setSharedContentWithNode((PNode) children.get(0));
                    else
                        node.setContent(false, new PNode(Set.of(0)));
//                        node.setContent(false, createNewContent(node.decodeDim(), false));
                }
                incEdgeRef(node, node.getContent());
                nodes.add(node.getContent());
                List<IContent> candidate = new ArrayList<>();
                for (IContent child : children)
                    candidate.add(((PNode) child).getContent());
                candidates.add(candidate);
            }
        }
        for(int i=0;i<nodes.size();i++) {
            incRef((PNode)nodes.get(i));
            updateContent((PNode)nodes.get(i),candidates.get(i));
        }

    }

    private Tuple2<List<IContent>, List<List<IContent>>> addCuboidChildren(List<IContent> nodes, List<List<IContent>> candidates, int depth, int new_layer) {
        Tuple2<List<IContent>, List<List<IContent>>> back = new Tuple2<>(null, null);
        if(depth == new_layer) {
            for(IContent node: nodes)
                incRef((PNode)node);
            back.x = nodes;
            back.y = candidates;
            return back;
        }
        List<IContent> nnodes = new ArrayList<>();
        List<List<IContent>> ncandi = new ArrayList<>();
        for(int i = 0;i<nodes.size();i++) {
            PNode node = (PNode) nodes.get(i);
            incRef(node);
            List<IContent> children = new ArrayList<>();
            for(IContent content:candidates.get(i))
                children.addAll(((PNode)content).getChildren());
            HashMap<Set<Integer>,List<IContent>> nchildren = new HashMap<>();
            for(IContent child : children) {
                if(!nchildren.containsKey(((PNode)child).getLabel()))
                    nchildren.put(((PNode)child).getLabel(), new ArrayList<>());
                nchildren.get(((PNode)child).getLabel()).add(child);
            }
            for(Map.Entry<Set<Integer>, List<IContent>> entry : nchildren.entrySet()) {
                Set<Integer> key = entry.getKey();
                children = entry.getValue();
                PNode child = (PNode) node.getChild(key);
                if(child==null)
                    if(children.size()==1)
                        child = (PNode) node.addChildNode((PNode) children.get(0), true);
                    else
                        child = (PNode) node.addChildNode(new PNode(Set.of(0)), false);
                incEdgeRef(node, node.getChild(key));
                nnodes.add(child);
                ncandi.add(children);
            }
        }
        return addCuboidChildren(nnodes, ncandi, depth+1, new_layer);
    }

    public void deleteCuboid(List<Integer> cuboid) {
        deleteDFS(root, 0, cuboid, 0);
    }

    private void deleteDFS(IContent rootContent, int dimension, List<Integer> cuboid, int depth) {
        PNode root = (PNode)rootContent;
        if(depth == cuboid.get(dimension) && dimension <  cuboid.size()-1) {
            deleteDFS(root.getContent(), dimension+1, cuboid, 0);
            if(((PNode)root.getContent()).nodeCount == 0)
                root.setContent(false, null);
        } else {
            for(int i=0;i<root.getChildren().size();i++) {
                PNode child = (PNode) root.getChildren().get(i);
                deleteDFS(child, dimension, cuboid, depth+1);
                if(child.nodeCount == 0) {
                    root.getChildren().remove(child);
                    i--;
                }
            }
        }
        root.nodeCount--;
    }

    private void getChildrenRec(IContent content, int depth, Stack<IContent> children) {
        if(depth == 0) {
            children.add(content);
            return;
        }
        if (content != null && ((PNode)content).getChildren() != null) {
            for(PNode child: ((PNode)content).getChildren())
                getChildrenRec(child, depth-1,children);
        }
    }

    private void incEdgeRef(PNode node, IContent content) {
        //TODO
        //node.ASN++;
        //((PNode)content).ASN--;
    }

    private void incRef(PNode node) {
        node.nodeCount++;
    }

    private void updateContent(PNode node, List<IContent> candidate){
        TableCuboid content = getCuboidInstance();
        for(IContent last_node: candidate) {
            TableCuboid cuboid = (TableCuboid)((PNode)last_node).getContent();
            content.merge(cuboid);
        }
        node.setContent(false, content);
    }

    private TableCuboid checkContentNull(TableCuboid result, PNode root, int dimension, List<List<Set<Integer>>> query) {
        IContent content = root.getContent();
        if (content == null) {
            if(root.getChildren() == null) {
//                System.out.println("????");
                return result;
            }
            for (PNode child : root.getChildren()) {
                checkContentNull(result, child, dimension, query);
            }
            return result;
        } else {
            if (dimension == query.size() - 1)
                result.merge((TableCuboid) content);
            else
                return queryDFS((PNode)content, result, query, dimension + 1);
        }
        return result;
    }


    public TableCuboid getCuboidInstance() {
        return new TableCuboid();
    }

    private void add(PNode root, TabularDataPoint dataPoint, int dimension, Set<IContent> updatedNodes){
        List<Set<Integer>> labels = dataPoint.getLabels().get(dimension);
        List<PNode> dimensionPathNodes = trailProperDimensionPath(root, labels, dimension);
        PNode child = null;
        // start with finest level ...
        int size = dimensionPathNodes.size() - 1;
        for (int i = size; i >= 0; i--) {
            PNode pathNode = dimensionPathNodes.get(i);
            if (i == size || pathNode.getContent() != null) {
                boolean isSum = dimension == dataPoint.getDimension() - 1;
                boolean update = processDimensionPathNode(pathNode, child, dimension, updatedNodes, isSum);
                if (update) {
                    if (isSum) {
                        if (pathNode.getContent() instanceof TableCuboid cuboid)
                            cuboid.insert(dataPoint);
                        else
                            throw new IllegalArgumentException("error cuboid");
                    } else {
                        if (pathNode.getContent() instanceof PNode content)
                            add(content, dataPoint, dimension + 1, updatedNodes);
                        else
                            throw new IllegalArgumentException("error content");
                    }
                    updatedNodes.add(pathNode.getContent());
                }
                child = pathNode;
            }
        }
    }

    private boolean processDimensionPathNode(PNode node, PNode child, int dimension, Set<IContent> updatedNodes, boolean isSum) {
        if (node.getChildrenSize() == 1) {
            node.setSharedContentWithNode(child);
        } else if (node.getContent() == null) {
            node.setContent(false, createNewContent(dimension + 1, isSum));
            return true;
        } else if (node.isContentShared() && !updatedNodes.contains(node.getContent())) {
            var shallowCopy = node.getContent().shallowCopy();
            node.setContent(false, shallowCopy);
            return true;
        } else return !node.isContentShared();
        return false;
    }

    private IContent createNewContent(int dimension, boolean isSum) {
        if (isSum) {
            return getCuboidInstance();
        } else {
            return new PNode(Set.of(0));
        }
    }

    private List<PNode> trailProperDimensionPath(PNode root, List<Set<Integer>> labels, int dimension) {
        List<PNode> stack = new ArrayList<>();
        stack.add(root);
        PNode node = root;
        for (int i =0;i<labels.size();i++) {
            PNode child = getOrCreateProperChildNode(node, labels.get(i), dimension, i);
            stack.add(child);
            node = child;
        }
        return stack;
    }

    private PNode getOrCreateProperChildNode(PNode node, Set<Integer> label, int dimension, int level) {
        PNode child = node.getChild(label);
        if (child == null) {
            return node.newProperChild(label);
        } else if (node.isChildShared(label)) {
            PNode copy = (PNode) child.shallowCopy();
            node.replaceChild(copy);
            return copy;

        } else {
            return child;
        }
    }
}
