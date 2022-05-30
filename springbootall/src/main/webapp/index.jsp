import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.RequestMapping;

@Controller
public class JspController {

    @RequestMapping("/main")
    public String main(Model model) {
        model.addAttribute("data", "springboot打包为war文件");
        return "index";
    }
}