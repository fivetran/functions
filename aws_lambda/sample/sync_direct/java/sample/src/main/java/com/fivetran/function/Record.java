package com.fivetran.function;

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