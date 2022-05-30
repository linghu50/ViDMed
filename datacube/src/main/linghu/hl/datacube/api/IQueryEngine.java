package main.linghu.hl.datacube.api;

import main.linghu.hl.datacube.api.utils.tuples.Tuple2;
import main.linghu.hl.datacube.api.utils.tuples.Tuple3;

import java.util.Date;
import java.util.List;

public interface IQueryEngine {
    List<Tuple3<Double, Double, Integer>> queryMap(double ltLat, double ltLon, double rbLat, double rbLon, int zoom, List<List<Long>> cate, Date from, Date to);
    List<Tuple2<Integer, Integer>> queryTime(double ltLat, double ltLon, double rbLat, double rbLon, int zoom, List<List<Long>> cate, int timeLevel);
}
