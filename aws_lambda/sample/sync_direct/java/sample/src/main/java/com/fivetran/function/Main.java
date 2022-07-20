package com.fivetran.function;

import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;

public class Main implements RequestHandler<Request, Response> {
    @Override
    public Response handleRequest(Request request, Context context) {
        return apiResponse(request.state, request.secrets);
    }

    Response apiResponse(Object state, Object secrets) {
        Record record1 = new Record(Instant.parse("2017-12-31T05:12:05Z"), 1001L, "$1200", "$12");
        Record record2 = new Record(Instant.parse("2017-12-31T06:12:04Z"), 1001L, "$1200", "$12");
        Record record3 = new Record(Instant.parse("2017-12-31T05:12:05Z"), 1000L, "$1200", "$12");
        Record record4 = new Record(Instant.parse("2017-12-31T06:12:04Z"), 1000L, "$1200", "$12");
        HashMap<String, Instant> newState = new HashMap<>();
        newState.put("transactionCursor", Instant.parse("2018-01-01T00:00:00Z"));
        state = newState;
        List<Record> records = new ArrayList<>();
        records.add(record1);
        records.add(record2);
        Map<String, Object> insert = new HashMap<>();
        insert.put("transactions", records);
        records.clear();
        records.add(record3);
        records.add(record4);
        Map<String, Object> delete = new HashMap<>();
        delete.put("transactions", records);
        List<String> primaryKey = new ArrayList<>();
        primaryKey.add("order_id");
        primaryKey.add("date");
        Map<String, List<String>> transactionsSchema = new HashMap<>();
        transactionsSchema.put("primary_key", primaryKey);
        Map<String, Object> schema = new HashMap<>();
        schema.put("transactions", transactionsSchema);
        return new Response(state, insert, delete, schema, true);
    }
}
