package main.linghu.hl.datacube.api.tree;

import java.util.List;

public interface ISerialized {
    List<Long> serializedBasicTree();
    void deSerializedBasicTree(List<Long> data);
}
