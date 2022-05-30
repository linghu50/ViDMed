package main.linghu.hl.datacube.PrivacyCube;

import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class Excel {
    public List<header> headers;    // 表头（属性名）
    public List<Map<String, Object>> desserts;  // 内容（每一行，字典型，{key:value}
    public Map<Integer, Map<String, Object>> modified = new HashMap<>();
    public Set<Integer> removed = new HashSet<>();

    public static class header {
        public String name;
        public Type type;
    }

    public enum Type {
        NUMBER,
        CATEGORICAL,
        TEMPORAL,
        SPATIAL,
    }
}



