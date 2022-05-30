package main.linghu.MPRU;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.builder.SpringApplicationBuilder;
import org.springframework.boot.web.servlet.support.SpringBootServletInitializer;
import static org.springframework.boot.SpringApplication.*;

@SpringBootApplication
public class TpaApplication extends SpringBootServletInitializer{
    public static void main(String[] args) {
        SpringApplication.run(TpaApplication.class,args);
    }

    @Override
    protected SpringApplicationBuilder configure(SpringApplicationBuilder builder) {
        return builder.sources(TpaApplication.class);
    }
}
