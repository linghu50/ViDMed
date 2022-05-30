package linghu.MPRU.service;

import main.linghu.hl.datacube.PrivacyCube.Excel;
import main.linghu.hl.datacube.PrivacyCube.Operators.IOperator;
import main.linghu.hl.datacube.PrivacyCube.PrivacyCube;
import main.linghu.hl.datacube.PrivacyCube.TabularDataPoint;
import main.linghu.hl.datacube.PrivacyCube.WebNode;
import org.apache.commons.math3.ml.distance.EarthMoversDistance;

import java.util.*;

public class TpaSession {
    public String token;
    public Excel excel;
    public PrivacyCube cube;
    public List<Integer> schema;
    public List<Integer> sensitive;
    public WebNode root;
    public List<IOperator> operators;

    public TpaSession(Excel excel) {
        token = UUID.randomUUID().toString();
        this.excel = excel;
        reloadCube();
    }

    public void reloadCube() {
        if (cube == null ) {
            cube = new PrivacyCube(excel.headers.size());
        } else {
            cube = new PrivacyCube(cube.schemaMap,excel.headers.size());
        }
        // 循环将Excel中的每行数据读入PrivacyCube结构中
        for (int i = 0; i < excel.desserts.size(); i++) {
            if (excel.removed.contains(i)) continue;
            Map<String, Object> data = excel.modified.get(i);
            cube.insert(new TabularDataPoint(excel.headers, data == null ? excel.desserts.get(i) : data, cube.schemaMap, i));
            //System.out.println(i);
        }
        operators = new ArrayList<>();
        System.out.println("loadCube");
    }

    public void updateRoot() {
        if (this.schema != null && this.sensitive != null) {
            this.root = this.cube.getWebTree(this.schema, this.sensitive, new EarthMoversDistance());
            this.operators.forEach(op->op.execute(this.root, this.schema));
        }
    }

    public  void highlightRoot(List<Set<Integer>> labels){
        if (this.schema != null && this.sensitive != null) {
            this.root = this.cube.highlightWebTree(this.schema, this.sensitive, labels, new EarthMoversDistance());
            this.operators.forEach(op->op.execute(this.root, this.schema));
        }
    }

    public double privacyCalculate(List<Integer> schema) {
        if (this.schema != null) {
            WebNode calculateRoot = this.cube.getWebTree(schema, new ArrayList<>(), new EarthMoversDistance());
            double cer = this.cube.calculate(calculateRoot);
            // 修改映射范围
            cer = (cer - 0.5) / 0.5;
            return cer;
        }
        return 0;
    }

    public void dispose(){
    }
}
