package com.example;

import java.util.*;

public class Record {
  public Boolean hasMore;
  public Map<String, List<Map<String, Object> > > insert;
  public Map<String, Map<String, List<String> > > schema;
  public Map<String, Object> state;
  public Record(Object since, List<Map<String,Object> > timeline) {
    this.hasMore = false;
    this.insert = new HashMap<>();
    this.insert.put("tflLineStatus",timeline);
    this.schema = new HashMap<>();
    Map<String, List<String> > pk = new HashMap<>();
    List<String> pkEntry = new ArrayList<>();
    pkEntry.add("linename");
    pk.put("primary_key",pkEntry );
    this.schema.put("tflLineStatus",pk);
    this.state = new HashMap<>();
    this.state.put("since_id",since);
  }
  public Record(){
    
  }
}
