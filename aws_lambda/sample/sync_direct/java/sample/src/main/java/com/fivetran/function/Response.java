package com.fivetran.function;
import java.util.Map;
public class Response {
    public Object state;
    public Map<String, Object> insert;
    public Map<String, Object> delete;
    public Map<String, Object> schema;
    public boolean hasMore;
    
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
}