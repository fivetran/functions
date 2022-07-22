package com.fivetran.function;

import java.util.Map;

public class Response {
    public Object state;
    public Map<String, Object> schema;
    public boolean hasMore;

    public Response(
            Object state,
            Map<String, Object> schema,
            boolean hasMore) {
        this.state = state;
        this.schema = schema;
        this.hasMore = hasMore;
    }
}