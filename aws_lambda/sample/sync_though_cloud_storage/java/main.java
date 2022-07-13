import java.time.Instant;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
public class LambdaFunctionHandler implements RequestHandler<Request, Response> {
    private static final ObjectMapper MAPPER = new ObjectMapper();
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
public class Request {
    Object state;
    Object secrets;
    public Object getState() {
        return state;
    }
    public void setState(Object state) {
        this.state = state;
    }
    public Object getSecrets() {
        return secrets;
    }
    public void setSecrets(Object secrets) {
        this.secrets = secrets;
    }
    public Request(Object state, Object secrets) {
        this.state = state;
        this.secrets = secrets;
    }
    public Request() {
    }
}
import java.util.Map;
public class Response {
    Object state;
    Map<String, Object> insert;
    Map<String, Object> delete;
    Map<String, Object> schema;
    boolean hasMore;
    public Object getState() {
        return state;
    }
    public void setState(Object state) {
        this.state = state;
    }
    public Map<String, Object> getInsert() {
        return insert;
    }
    public void setDelete(Map<String, Object> insert) {
        this.insert = insert;
    }
    public Map<String, Object> getDelete() {
        return delete;
    }
    public void setSchema(Map<String, Object> delete) {
        this.delete = delete;
    }
    public Map<String, Object> getSchema() {
        return schema;
    }
    public void setInsert(Map<String, Object> schema) {
        this.schema = schema;
    }
    public boolean getHasMore() {
        return hasMore;
    }
    public void setHasMore(boolean hasMore) {
        this.hasMore = hasMore;
    }
    public Response(
            Object state,
            Map<String, Object> insert,
            Map<String, Object> delete,
            Map<String, Object> schema,
            boolean hasMore) {
        this.state = state;
        this.insert = insert;
        this.delete = delete;
        this.schema = schema;
        this.hasMore = hasMore;
    }
    public Response() {
    }
}
import java.time.Instant;
public class Record {
    public Instant date;
    public Long order_id;
    public String amount;
    public String discount;
    public Record(Instant date, Long order_id, String amount, String discount) {
        this.date = date;
        this.order_id = order_id;
        this.amount = amount;
        this.discount = discount;
    }
}