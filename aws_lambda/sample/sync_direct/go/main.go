package main

import (
	"github.com/aws/aws-lambda-go/lambda"
)

type Request struct {
	State   map[string]string `json:"state"`
	Secrets map[string]string `json:"secrets"`
}

type Response struct {
	State   map[string]string   `json:"state"`
	Insert  map[string][]Record `json:"insert"`
	Delete  map[string][]Record `json:"delete"`
	Schema  map[string]Key      `json:"schema"`
	HasMore bool                `json:"hasMore"`
}

type Key struct {
	PrimaryKey []string `json:"primary_key"`
}

type Record struct {
	Date     string `json:"date"`
	OrderId  int    `json:"order_id"`
	Amount   string `json:"amount"`
	Discount string `json:"discount"`
}

func handleLambdaEvent(request Request) (Response, error) {
	insertTransactions, deleteTransactions, newTransactionsCursor := apiResponse(request.State, request.Secrets)
	newState := make(map[string]string)
	newState["transactionsCursor"] = newTransactionsCursor
	primary_key := make([]string, 0)
	primary_key = append(primary_key, "order_id")
	primary_key = append(primary_key, "date")
	transactionsSchema := make(map[string]Key)
	transactionsSchema["transactions"] = Key{PrimaryKey: primary_key}
	return Response{State: newState, Insert: insertTransactions, Delete: deleteTransactions, Schema: transactionsSchema, HasMore: false}, nil
}

func apiResponse(state map[string]string, secrets map[string]string) (map[string][]Record, map[string][]Record, string) {
	insertTransactions := make(map[string][]Record)
	insertTransactions["transactions"] = append(insertTransactions["transactions"], Record{Date: "2017-12-31T05:12:05Z", OrderId: 1001, Amount: "$1200", Discount: "$12"})
	insertTransactions["transactions"] = append(insertTransactions["transactions"], Record{Date: "2017-12-31T05:12:05Z", OrderId: 1002, Amount: "$1345", Discount: "$14"})
	deleteTransactions := make(map[string][]Record)
	deleteTransactions["transactions"] = append(deleteTransactions["transactions"], Record{Date: "2017-12-31T05:12:05Z", OrderId: 1001, Amount: "$1200", Discount: "$12"})
	return insertTransactions, deleteTransactions, "2018-01-01T00:00:00Z"
}

func main() {
	lambda.Start(handleLambdaEvent)
}
