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
import com.google.gson.*;


public class Example implements HttpFunction {

    @Override
    public void service(HttpRequest request, HttpResponse response) throws Exception {
        Record res = apiResponse();
        String recordJSONString = new Gson().toJson(res);

        Writer out = response.getWriter();
        response.setContentType("application/json");
        out.write(recordJSONString);
    }

    private Record apiResponse() throws Exception {
        URL url = new URL("https://api.tfl.gov.uk/line/mode/tube/status");

        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");
        conn.connect();

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
        Object since = ((JSONObject) data.get(0)).get("id");
        List<Map<String, Object>> timeline = new ArrayList<>();

        for (int i = 0; i < data.size(); i++) {
            JSONObject sub = (JSONObject) data.get(i);
            Map<String, Object> linesDetailMap = new HashMap<>();
            linesDetailMap.put("linename", sub.get("id"));
            linesDetailMap.put("linestatus", ((JSONObject) ((JSONArray) sub.get("lineStatuses")).get(0)).get("statusSeverityDescription"));
            linesDetailMap.put("timestamp", sub.get("created"));
            timeline.add(linesDetailMap);
        }

        // insert
        Map<String, List<Map<String, Object>>> insert = new HashMap<>();
        insert.put("tflLineStatus", timeline);

        // schema
        Map<String, Map<String, List<String>>> schema = new HashMap<>();
        Map<String, List<String>> primary_key_map = new HashMap<>();
        List<String> primary_key_list = new ArrayList<>();
        primary_key_list.add("linename");
        primary_key_map.put("primary_key", primary_key_list);
        schema.put("tflLineStatus", primary_key_map);

        //state
        Map<String, Object> state = new HashMap<>();
        state.put("since_id", since);

        Record record = new Record(since, insert, schema, state, false);
        return record;

    }

    private class Record {
        public Boolean hasMore;
        public Map<String, List<Map<String, Object>>> insert;
        public Map<String, Map<String, List<String>>> schema;
        public Map<String, Object> state;

        public Record(Object since, Map<String, List<Map<String, Object>>> insert, 
                        Map<String, Map<String, List<String>>> schema, 
                        Map<String, Object> state, 
                        Boolean hasMore) {
            this.hasMore = hasMore;
            this.insert = insert;
            this.schema = schema;
            this.state = state;
        }
    }
}


