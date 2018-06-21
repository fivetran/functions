Elastic search instance setup
===========================
1. Create an elastic search instance
2. Insert sample records in elastic search
	
	`curl -XPOST <your_elastic_search_host_name>/_bulk?pretty --data-binary @elastic_search_records.json -H 'Content-Type: application/json'`
3. Test records in elastic search
	
	`curl -XGET '<your_elastic_search_host_name>/products/_search?q=Bag'`

Lambda function setup
===========================
1. Create a directory (elastic_search_function)
2. Install elastic search in the directory
	`npm install elasticsearch`
3. Create a zip file
	`zip -r elastic_search_function.zip *`
4. Create a Lambda function.
   
   For elastic search, execution role must have policy
	```
	{
      "Version": "2012-10-17",
      "Statement": [
        {
            "Action": [
                "es:*"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
     ]
   }
	``` 
4. Upload Lambda function
5. Create a test sample with request
	```
	{
	  "state" : {},
          "secrets" : {
		"host" : "your_elastic_search_host_name"
	  }
	}
	```
6. Run test to fetch records
