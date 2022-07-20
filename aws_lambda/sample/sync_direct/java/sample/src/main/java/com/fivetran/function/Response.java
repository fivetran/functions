package com.fivetran.function;
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