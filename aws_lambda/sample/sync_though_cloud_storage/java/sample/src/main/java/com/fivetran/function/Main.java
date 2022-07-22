package com.fivetran.function;

import com.amazonaws.SdkClientException;
import com.amazonaws.regions.Regions;
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Main implements RequestHandler<Request, Response> {
    private static final ObjectMapper MAPPER = new ObjectMapper().registerModule(new JavaTimeModule());

    public Response handleRequest(final Request request, final Context context) {
        return this.apiResponse(request);
    }

    Response apiResponse(Request request) {
        Record record1 = new Record(Instant.parse("2017-12-31T05:12:05Z"), 1001L, "$1200", "$12");
        Record record2 = new Record(Instant.parse("2017-12-31T06:12:04Z"), 1001L, "$1200", "$12");
        Record record3 = new Record(Instant.parse("2017-12-31T05:12:05Z"), 1000L, "$1200", "$12");
        Record record4 = new Record(Instant.parse("2017-12-31T06:12:04Z"), 1000L, "$1200", "$12");
        HashMap<String, Instant> newState = new HashMap<>();
        newState.put("transactionCursor", Instant.parse("2018-01-01T00:00:00Z"));
        request.state = newState;

        //insert records
        List<Record> records = new ArrayList<>();
        records.add(record1);
        records.add(record2);
        Map<String, Object> insert = new HashMap<>();
        insert.put("transactions", records);

        //delete records
        records = new ArrayList<>();
        records.add(record3);
        records.add(record4);
        Map<String, Object> delete = new HashMap<>();
        delete.put("transactions", records);

        // schema
        List<String> primaryKey = new ArrayList<>();
        primaryKey.add("order_id");
        primaryKey.add("date");
        Map<String, List<String>> transactionsSchema = new HashMap<>();
        transactionsSchema.put("primary_key", primaryKey);
        Map<String, Object> schema = new HashMap<>();
        schema.put("transactions", transactionsSchema);

        this.pushToS3(request.bucket, request.file, this.jsonString(insert, delete));
        return new Response(request.state, schema, true);
    }

    private String jsonString(final Map<String, Object> insert, final Map<String, Object> delete) {
        try {
            return Main.MAPPER.writeValueAsString(Map.of("insert", insert, "delete", delete));
        } catch (JsonProcessingException e) {
            throw new RuntimeException("Failed while generating json", e);
        }
    }

    private void pushToS3(final String bucket, final String objKey, final String json) {
        try {
            //we need to specify the bucket region here if bucket is not global & `lambda` in not the same region as s3 bucket
            AmazonS3 s3Client = AmazonS3ClientBuilder.standard().withRegion(Regions.AP_SOUTH_1).build();
            s3Client.putObject(bucket, objKey, json);
        } catch (SdkClientException e) {
            throw new RuntimeException(String.format("Failed while pushing %s object to %s bucket", objKey, bucket), e);
        }
    }
}
