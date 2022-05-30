package main.linghu.hl.datacube.PrivacyCube.Operators;

import main.linghu.hl.datacube.PrivacyCube.WebNode;

import java.util.List;

public interface IOperator {
    boolean execute(WebNode root, List<Integer> schema);
}
