package main

import (
	"bytes"
	"context"
	"encoding/json"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/s3/s3manager"
	"os"
)

type Request struct {
	State   map[string]string `json:"state"`
	Secrets map[string]string `json:"secrets"`
	Bucket  string            `json:"bucket"`
	File    string            `json:"file"`
}

type Response struct {
	State   map[string]string `json:"state"`
	Schema  map[string]Key    `json:"schema"`
	HasMore bool              `json:"hasMore"`
}

type S3Response struct {
	Insert map[string][]Record `json:"insert"`
	Delete map[string][]Record `json:"delete"`
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

	json := generateJson(insertTransactions, deleteTransactions)
	uploadToS3(request.Bucket, request.File, json)

	return Response{State: newState, Schema: transactionsSchema, HasMore: false}, nil
}

func apiResponse(state map[string]string, secrets map[string]string) (map[string][]Record, map[string][]Record, string) {
	insertTransactions := make(map[string][]Record)
	insertTransactions["transactions"] = append(insertTransactions["transactions"], Record{Date: "2017-12-31T05:12:05Z", OrderId: 1001, Amount: "$1200", Discount: "$12"})
	insertTransactions["transactions"] = append(insertTransactions["transactions"], Record{Date: "2017-12-31T05:12:05Z", OrderId: 1002, Amount: "$1345", Discount: "$14"})
	deleteTransactions := make(map[string][]Record)
	deleteTransactions["transactions"] = append(deleteTransactions["transactions"], Record{Date: "2017-12-31T05:12:05Z", OrderId: 1001, Amount: "$1200", Discount: "$12"})
	return insertTransactions, deleteTransactions, "2018-01-01T00:00:00Z"
}

func generateJson(insert map[string][]Record, delete map[string][]Record) []byte {
	response := &S3Response{Insert: insert, Delete: delete}
	json, err := json.Marshal(response)

	if err != nil {
		panic(err)
	}

	return json
}

func uploadToS3(bucket string, file string, json []byte) {
	// create session and uploader
	s3Config := &aws.Config{
		//we need to specify the bucket region here if bucket is not global & `lambda` in not the same region as s3 bucket
		Region:      aws.String(os.Getenv("AWS_REGION")), 
	}
	s3Session := session.New(s3Config)
	uploader := s3manager.NewUploader(s3Session)

	// uploading
	input := &s3manager.UploadInput{
		Bucket:      aws.String(bucket),
		Key:         aws.String(file),
		Body:        bytes.NewReader(json),
		ContentType: aws.String("json"),
	}
	_, err := uploader.UploadWithContext(context.Background(), input)

	if err != nil {
		panic(err)
	}
}

func main() {
	lambda.Start(handleLambdaEvent)
}
