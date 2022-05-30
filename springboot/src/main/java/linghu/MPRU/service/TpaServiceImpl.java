package linghu.MPRU.service;

import main.linghu.hl.datacube.PrivacyCube.Excel;
import main.linghu.hl.datacube.PrivacyCube.Operators.MergeCOP;
import main.linghu.hl.datacube.PrivacyCube.Operators.MergeOP;
import main.linghu.hl.datacube.PrivacyCube.Operators.UpdateOP;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import linghu.MPRU.resutl.Result;

import java.text.NumberFormat;
import java.util.*;

public class TpaServiceImpl {
    public static TpaServiceImpl INSTANCE = new TpaServiceImpl();
    private final Logger logger = LoggerFactory.getLogger(this.getClass());
    private final Map<String, TpaSession> activeExcel;

    private TpaServiceImpl() {
        activeExcel = new HashMap<>();
    }

    public Result  uploadExcel(String token, Excel excel){
        long st = System.currentTimeMillis();   // 获得当前时间
        if(activeExcel.containsKey(token)) {    // 如果原先有Excel则删除
            activeExcel.get(token).dispose();   // 释放内存（但是这里的dispose没有写具体实现）
            activeExcel.remove(token);  // 删除
        }
        TpaSession newSession = new TpaSession(excel);  // 这里需要进一步看看 *******************************
        activeExcel.put(newSession.token, newSession);
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("token", newSession.token);
        result.put("mapSchema", newSession.cube.schemaMap);
        logger.info("[uploadExcel]{%s}[%d]: %s".formatted(token, System.currentTimeMillis() - st, newSession.token));
        return new Result(200, "uploadExcel", result);
    }

    public Result updateTableau(String token, UpdateOP op) {
        long st = System.currentTimeMillis();
        if(checkActive(token)) {
            TpaSession session = activeExcel.get(token);
            op.execute(session.excel);  // 操作session中的Excel表格（op可以是合并，在页面中将某个属性拖拽到另一属性上松开，则两个属性合并（此时两个属性应该都是折叠态））
            session.reloadCube();   // 这一步修改了PrivacyTree的root
            session.updateRoot();
            logger.info("[updateTableau]{%s}[%d][]: %s".formatted(token, System.currentTimeMillis() - st, op));
            return new Result(200, "updateSchema", session.root);
        } else {
            logger.info("[updateTableau]{%s}[%d][]: failed - no session".formatted(token, System.currentTimeMillis() - st));
            return new Result(400, "updateSchema",null);
        }
    }

    public Result updateSchema(String token, List<Integer> schema, List<Integer> sensitive) {
        long st = System.currentTimeMillis();
        if(checkActive(token)) {
            TpaSession session = activeExcel.get(token);
            session.schema = schema;
            session.sensitive = sensitive;
            session.updateRoot();
            logger.info("[updateSchema]{%s}[%d][]: %s %s".formatted(token, System.currentTimeMillis() - st, schema, sensitive));
            return new Result(200, "updateSchema", session.root);   // 返回的是webTree的root
        } else {
            logger.info("[updateSchema]{%s}[%d][]: failed - no session".formatted(token, System.currentTimeMillis() - st));
            return new Result(400, "updateSchema",null);
        }
    }

    public Result highlightSchema(String token, List<Integer> schema, List<Integer> sensitive,
                                  List<Set<Integer>> labels) {
        long st = System.currentTimeMillis();
        if(checkActive(token)) {
            TpaSession session = activeExcel.get(token);
            session.schema = schema;
            session.sensitive = sensitive;
            session.highlightRoot(labels);
            logger.info("[highlightSchema]{%s}[%d][]: %s %s %s".formatted(token, System.currentTimeMillis() - st,
                    schema,
                    sensitive, labels));
            return new Result(200, "highlightSchema", session.root);   // 返回的是webTree的root
        } else {
            logger.info("[highlightSchema]{%s}[%d][]: failed - no session".formatted(token,
                    System.currentTimeMillis() - st));
            return new Result(400, "highlightSchema",null);
        }
    }

    public Result privacyAssess(String token, List<Integer> schema) {
        long st = System.currentTimeMillis();
        if(checkActive(token)) {
            TpaSession session = activeExcel.get(token);
            session.schema = schema;
            double cer = session.privacyCalculate(schema);
            NumberFormat nf = NumberFormat.getNumberInstance();
            nf.setMinimumFractionDigits(4);
            logger.info("[privacyAssess]{%s}[%d][]: %s %s".formatted(token, System.currentTimeMillis() - st,
                    schema,  nf.format(cer)));

            session.schema = null;
            return new Result(200, "privacyAssess", nf.format(cer));   // 返回的是信息熵
        } else {
            logger.info("[privacyAssess]{%s}[%d][]: %s".formatted(token, System.currentTimeMillis() - st,
                    schema));
            return new Result(400, "privacyAssess",null);
        }
    }

    public Result mergeGroup(String token, MergeOP op){
        long st = System.currentTimeMillis();
        if(checkActive(token)) {
            TpaSession session = activeExcel.get(token);
            activeExcel.get(token).operators.add(op);
            if(!op.execute(session.root, session.schema)) {
                logger.info("[mergeGroup]{%s}[%d][]: failed - execute op".formatted(token, System.currentTimeMillis() - st));
                return new Result(401, "mergeGroup", null);
            }
            logger.info("[mergeGroup]{%s}[%d][]: %s %d %s %s".formatted(token, System.currentTimeMillis() - st, op.filters, op.dim, op.label1, op.label2));
            return new Result(200, "mergeGroup", session.root);
        } else {
            logger.info("[mergeGroup]{%s}[%d][]: failed - no session".formatted(token, System.currentTimeMillis() - st));
            return new Result(400, "mergeGroup",null);
        }
    }

    public Result mergeCubeGroup(String token, MergeCOP op){
        long st = System.currentTimeMillis();
        if(checkActive(token)) {
            TpaSession session = activeExcel.get(token);
            if(!op.execute(session.cube)) {
                logger.info("[mergeCubeGroup]{%s}[%d][]: failed - execute op".formatted(token, System.currentTimeMillis() - st));
                return new Result(401, "mergeCubeGroup", null);
            }
            session.updateRoot();
            logger.info("[mergeCubeGroup]{%s}[%d][]: %s %d %s %s".formatted(token, System.currentTimeMillis() - st, op.filters, op.dim, op.label1, op.label2));
            return new Result(200, "mergeCubeGroup", session.root);
        } else {
            logger.info("[mergeCubeGroup]{%s}[%d][]: failed - no session".formatted(token, System.currentTimeMillis() - st));
            return new Result(400, "mergeCubeGroup",null);
        }
    }

    public boolean checkActive(String token) {
        return activeExcel.containsKey(token);
    }

}
