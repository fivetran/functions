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
import com.example.Record.*;


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
      
      //Using the JSON simple library parse the string into a json object
      // JSONParser parse = new JSONParser();
      // List<Object> timeline = new ArrayList<>();
      // JSONObject data = (JSONObject) parse.parse(inline);
      // HashMap<String,Object> result = new ObjectMapper().readValue(data, HashMap.class);
      // return result;

      JSONParser parse = new JSONParser();
      JSONArray data = (JSONArray) parse.parse(inline);
      Object since =  ((JSONObject) data.get(0)).get("id");
      System.out.println("#######.  " + since );
      List<Map<String,Object> > temp = new ArrayList<>();
      // Map<String,String> tempMap = new HashMap<>();
      // tempMap.put("A","a");
      // tempMap.put("B","b");
      // temp.add(tempMap);
      for(int i = 0;i<data.size();i++){
        JSONObject sub = (JSONObject) data.get(i);
        Map<String,Object> tempMap = new HashMap<>();
        tempMap.put("linename",sub.get("id"));
        tempMap.put("linestatus",((JSONObject) ((JSONArray) sub.get("lineStatuses")).get(0)).get("statusSeverityDescription"));
        tempMap.put("timestamp",sub.get("created"));
        temp.add(tempMap);
      }
      Record record = new Record(since, temp);

      return record;



    }catch(Exception e){
      return new Record();
    }
    
  }
}

