package linghu.MPRU.controller;

import main.linghu.hl.datacube.PrivacyCube.Excel;
import main.linghu.hl.datacube.PrivacyCube.Operators.MergeCOP;
import main.linghu.hl.datacube.PrivacyCube.Operators.MergeOP;
import main.linghu.hl.datacube.PrivacyCube.Operators.UpdateOP;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import linghu.MPRU.resutl.Result;
import linghu.MPRU.service.TpaServiceImpl;

import javax.servlet.http.HttpServletRequest;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@RestController
@CrossOrigin
public class TpaController {

    // 上传Excel文件（upload页面
    @PostMapping("uploadExcel")
    public Result uploadExcel(HttpServletRequest request, @RequestBody Excel excel) {
        //如果前端传递的对象是以json对象的形式传递的，那么后端再接收参数的时候，可以参数前使用@RequestBody注解
        return TpaServiceImpl.INSTANCE.uploadExcel(getToken(request), excel);
    }
    // 各种操作，目前知道有modify（在页面中将某个属性拖拽到另一属性上松开，则两个属性合并（此时两个属性应该都是折叠态）），add，remove
    // op是通过发包传送的，问题：如何发出这样的包
    @PostMapping("updateTableau")
    public Result updateTableau(HttpServletRequest request, @RequestBody UpdateOP op) {
        return TpaServiceImpl.INSTANCE.updateTableau(getToken(request), op);
    }

    // 属性排序以更新表单（sheet页面属性排序触发）
    @PostMapping("updateSchema")
    public Result getBasicTree(HttpServletRequest request,@RequestBody Map<String, List<Integer>> config) {
        return TpaServiceImpl.INSTANCE.updateSchema(getToken(request), config.get("schema"), config.get("sensitives"));
    }

    // 点击风险树圆环以显示该段表单（sheet页面风险树点击触发）
    @PostMapping("highlightSchema")
    public Result getHighlightTree(HttpServletRequest request,@RequestBody Map<String, ArrayList> config) {
        return TpaServiceImpl.INSTANCE.highlightSchema(getToken(request), config.get("schema"), config.get(
                "sensitives"),
                config.get("labels"));
    }

    @PostMapping("privacyAssess")
    public Result getPrivacyAssess(HttpServletRequest request,@RequestBody Map<String, List<Integer>> config) {
        return TpaServiceImpl.INSTANCE.privacyAssess(getToken(request), config.get("schema"));
    }

    @PostMapping("mergeOP")
    public Result mergeGroup(HttpServletRequest request,@RequestBody MergeOP op) {
        return TpaServiceImpl.INSTANCE.mergeGroup(getToken(request), op);
    }

    @PostMapping("MergeCOP")
    public Result mergeGroup(HttpServletRequest request,@RequestBody MergeCOP op) {
        return TpaServiceImpl.INSTANCE.mergeCubeGroup(getToken(request), op);
    }

    private static String getToken(HttpServletRequest request) {
        String token = request.getHeader("Access-Token");
        return token == null ? "" : token;
    }
}
