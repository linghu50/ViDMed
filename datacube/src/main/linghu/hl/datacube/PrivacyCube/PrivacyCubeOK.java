package main.linghu.hl.datacube.PrivacyCube;

import main.linghu.hl.datacube.api.IQueryEngine;
import main.linghu.hl.datacube.api.tree.IContent;
import main.linghu.hl.datacube.api.utils.tuples.Tuple2;
import org.apache.commons.math3.ml.distance.DistanceMeasure;

import java.util.*;
import java.util.stream.Collectors;

public class PrivacyCubeOK {
    public final PNode root;
    public final List<Tuple2<String, List<Object>>> schemaMap;
    public List<List<Integer>> cuboids = new ArrayList<>();

    public PrivacyCubeOK(int dimension) {
        this(new ArrayList<>(), dimension);
    }

    public PrivacyCubeOK(List<Tuple2<String, List<Object>>> schemaMap, int dimension) {
        root = new PNode(Set.of(0));
        this.schemaMap = schemaMap;
        int[] smartcubeConfig = new int[dimension];
        Arrays.fill(smartcubeConfig, 1);
        cuboids.add(Arrays.stream(smartcubeConfig).boxed().collect(Collectors.toList()));

    }
    // 从datacube中构造页面操作用的webtree
    public WebNode getWebTree(List<Integer> schema, List<Integer> sensitives, DistanceMeasure distanceMeasure) {
        Stack<WebNode> path = new Stack<>();
        WebNode child = new WebNode();
        child.labels.add(-1);
        path.push(child);
        List<List<Set<Integer>>> queries = new ArrayList<>();
        for (int i = 0; i < schemaMap.size(); i++) {
            // 第一遍什么都不查，但我要告诉你有几层查询层次，路都走一遍，以此构造出WebTree
            queries.add(new ArrayList<>());
        }
        List<double[]> globals = new ArrayList<>();
        // var 不是关键字，相当于一种动态类型，编译器根据变量所赋的值来推断类型。所以必须在定义变量的时候赋初始值
        var content = query(queries);
        for (Integer sensitive : sensitives) {
            // 获取该分类下的sensitive属性的分布情况
            globals.add(content.getDistribute(sensitive, schemaMap.get(sensitive).y.size()));
        }
        return dfsWebTree(schema, path, sensitives, globals, distanceMeasure);
    }

    private WebNode dfsWebTree(List<Integer> schema, Stack<WebNode> path, List<Integer> sensitives, List<double[]> globals, DistanceMeasure distanceMeasure) {
        WebNode root = path.peek(); // 获取栈顶元素
        List<List<Set<Integer>>> queries = new ArrayList<>();
        for (int i = 0; i < schemaMap.size(); i++) {
            boolean flag = true;
            for (int j = 0; j < schema.size(); j++) {
                // 如果轮到的排列属性是属性集中的这个，并且路径中已经走过这一级
                // 第一次进入dfsWebTree，path只有一个点，path.size() - 1 > j恒不成立，因而queries会在第一轮添加表格属性个空列表
                if (schema.get(j) == i && path.size() - 1 > j) {
                    List<Set<Integer>> query = new ArrayList<>();
                    query.add(path.get(j + 1).labels);
                    queries.add(query);
                    flag = false;
                }
            }
            if (flag) {
                // 表格属性，对应位置不在查询属性中，则在queries中添加空列表
                // 第一轮，恒添加空列表
                queries.add(new ArrayList<>());
            }
        }
        // 第一轮会将WebTree的root的content指向没有任何分类下的Tablecuboid，d下包含所有数据
        root.content = query(queries);
        if (root.content == null || root.content.inValid()) {
            return null;
        }

        // 该分类下k匿名即同样筛选条件下余留的组合数目，所以就是content中d的大小
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
            // 这里应该有点问题，这样是nanocube的方法，privacycube中content层是按表格顺序存储的以那个结点开始分类的情况，这里就是找到排列属性打头的PNode结点链条
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
        // query的作用是根据查询序列标签，找到最后一个点的content，比如[[][][]]就为所有筛选条件不限制，返回root的content
        // 如果有标签筛选，就按分类进入children，如果没有就进入content
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

        for(int i=0;i<new_schema.size();i++) {
            // 循环终止条件不应该-1，-1了，不到最后一层，会失败
            var back = addCuboidChildren(nodes,candidates,0,new_schema.get(i));
            List<IContent> next_nodes = back.x;
            List<List<IContent>> next_candi = back.y;
            // back的赋值方法错了，因为back.x=nodes，是浅拷贝，清除nodes的同时也清除了back
            nodes.clear();
            candidates.clear();
            for(int k=0;k<next_nodes.size();k++) {
                PNode node = (PNode) next_nodes.get(k);
                List<IContent> candi = next_candi.get(k);
                Stack<IContent> children = new Stack<>();   // 获取该结点的子节点
                for(int j=0;j<candi.size();j++) {
                    int depth = basic_schema.get(i)-new_schema.get(i);
                    getChildrenRec(candi.get(j), depth, children);
                }
                if (i != new_schema.size()-1){
                    if(node.getContent() == null) {
                        if(children.size() == 1)    // 分类只有一个，与子节点共享content
                            node.setSharedContentWithNode((PNode) children.get(0));
                        else
                            node.setContent(false, new PNode(Set.of(0)));   // 分类不止一个，新建content，但? 为什么增加为0的node,这里有问题
    //                        node.setContent(false, createNewContent(node.decodeDim(), false));
                    }
                    incEdgeRef(node, node.getContent());
                    nodes.add(node.getContent());
                }
                else{
                    nodes.add(node);
                }
                List<IContent> candidate = new ArrayList<>();
                for (IContent child : children)
                {
                    if (i == new_schema.size()-1)
                        candidate.add((child));
                    else
                        candidate.add(((PNode)child).getContent());
                }
                candidates.add(candidate);
                /*
                又改错了，为啥不对呢
                List<IContent> candidate = new ArrayList<>();
                for (IContent child : children)
                    candidate.add(((PNode) child).getContent());
                candidates.add(candidate);
                 */
            }
        }
        for(int i=0;i<nodes.size();i++) {
            incRef((PNode)nodes.get(i));
            updateContent((PNode)nodes.get(i),candidates.get(i));
        }

    }

    private Tuple2<List<IContent>, List<List<IContent>>> addCuboidChildren(List<IContent> nodes, List<List<IContent>> candidates, int depth, int new_layer) {
        Tuple2<List<IContent>, List<List<IContent>>> back = new Tuple2<>(new ArrayList<>(), new ArrayList<>());
        if(depth == new_layer) {
            for(IContent node: nodes)
                incRef((PNode)node);
            for(IContent node: nodes){
                back.x.add(node);
            }
            for (List<IContent> cand: candidates){
                back.y.add(cand);
            }
            // back的赋值方法错了，因为back.x=nodes，是浅拷贝，清除nodes的同时也清除了back
            //back.x = nodes;
            //back.y = candidates;
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
            if(((PNode)root.getContent()).ASN == 0)
                root.setContent(false, null);
        } else {
            for(int i=0;i<root.getChildren().size();i++) {
                PNode child = (PNode) root.getChildren().get(i);
                deleteDFS(child, dimension, cuboid, depth+1);
                if(child.ASN == 0) {
                    root.getChildren().remove(child);
                    i--;
                }
            }
        }
        root.ASN--;
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
        node.ASN++;
        ((PNode)content).ASN--;
    }

    private void incRef(PNode node) {
        node.ASN++;   // 结点的引用次数+1
    }

    private void updateContent(PNode node, List<IContent> candidate){
        TableCuboid content = getCuboidInstance();
        for(IContent last_node: candidate) {
            TableCuboid cuboid = (TableCuboid)(((PNode)last_node).getContent());
            content.merge(cuboid);
        }
        // 还有问题
        if (content.d != null) {
            node.setContent(false, content);
        }
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
            // 这个条件很重要，不加就和nanocube没区别了，但是记住是==null
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
