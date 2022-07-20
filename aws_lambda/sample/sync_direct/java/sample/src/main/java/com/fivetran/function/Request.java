package com.fivetran.function;

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