package com.example;

import com.google.cloud.functions.HttpFunction;
import com.google.cloud.functions.HttpRequest;
import com.google.cloud.functions.HttpResponse;
import java.util.HashMap;
import java.io.*;
import java.net.*;
import java.util.*;
import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.time.Instant;  
import com.google.gson.*;


public class Example implements HttpFunction {
  @Override
  public void service(HttpRequest request, HttpResponse response) throws Exception {
    Record res  = apiResponse();
    String recordJSONString = new Gson().toJson(res);

    Writer out = response.getWriter();
    response.setContentType("application/json");
    out.write(recordJSONString);
  }
  Record apiResponse() {
    try{
      URL url = new URL("https://api.tfl.gov.uk/line/mode/tube/status");

      HttpURLConnection conn = (HttpURLConnection) url.openConnection();
      conn.setRequestMethod("GET");
      conn.connect();

      //Getting the response code
      int responsecode = conn.getResponseCode();

      String inline = "";
      Scanner scanner = new Scanner(url.openStream());
    
      //Write all the JSON data into a string using a scanner
      while (scanner.hasNext()) {
          inline += scanner.nextLine();
      }
      
      //Close the scanner
      scanner.close();
      

      JSONParser parse = new JSONParser();
      JSONArray data = (JSONArray) parse.parse(inline);
      Object since =  ((JSONObject) data.get(0)).get("id");
      List<Map<String,Object> > timeline = new ArrayList<>();
 
      for(int i = 0;i<data.size();i++){
        JSONObject sub = (JSONObject) data.get(i);
        Map<String,Object> tempMap = new HashMap<>();
        tempMap.put("linename",sub.get("id"));
        tempMap.put("linestatus",((JSONObject) ((JSONArray) sub.get("lineStatuses")).get(0)).get("statusSeverityDescription"));
        tempMap.put("timestamp",sub.get("created"));
        timeline.add(tempMap);
      }

      
      Map<String, List<Map<String, Object> > > insert = new HashMap<>();
      insert.put("tflLineStatus",timeline);

      Map<String, Map<String, List<String> > > schema = new HashMap<>();
      Map<String, List<String> > pk = new HashMap<>();
      List<String> pkEntry = new ArrayList<>();
      pkEntry.add("linename");
      pk.put("primary_key",pkEntry );
      schema.put("tflLineStatus",pk);
      Map<String, Object> state = new HashMap<>();
      state.put("since_id",since);
      Record record = new Record(since, insert, schema, state);
      return record;

    }catch(Exception e){
      return new Record();
    }
    
  }

  public class Record {
    public Boolean hasMore;
    public Map<String, List<Map<String, Object> > > insert;
    public Map<String, Map<String, List<String> > > schema;
    public Map<String, Object> state;
    public Record(Object since, Map<String, List<Map<String, Object> > > insert, Map<String, Map<String, List<String> > > schema, Map<String, Object> state ) {
      this.hasMore = false;
      this.insert = insert;
      this.schema = schema;
      this.state = state;
    }
    public Record(){
      
    }
  }
}


