package main.linghu.hl.datacube.Linkube;

import main.linghu.hl.datacube.api.tree.INode;


public interface ILode extends INode, ILink<ILode> {
    int getCount();
    void setCount(int count);
    void updateCount();
    int getChildrenCount();
    ILode getLeftMostChild();
    ILode getRightMostChild();
    ILink<?> getContent();
    @Override
    ILode getNextNode();
    @Override
    ILode shallowCopy();
}
