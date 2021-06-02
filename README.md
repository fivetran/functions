# Fivetran

[Fivetran](https://fivetran.com/) helps you centralize data from disparate sources into your data storage platform that you can manage directly from your browser. Fivetran’s fully automated connectors extract your data from cloud applications, databases, event logs, and more, and load the data into your cloud warehouse, database, or data lake.

## Fivetran Cloud Function Connectors

[Function connectors](https://fivetran.com/docs/functions) allow you to code a custom data connector as an extension of Fivetran. If you have a custom data source or a private API, use our Function connectors to build robust serverless ELT data pipelines. You only have to write the cloud function to extract the data from your source. Fivetran will load and transform the data in your destination. 

## Get Started

[Create you Fivetran account](https://fivetran.com/signup?email=) and get started.

## Supported Platforms

Fivetran supports the following cloud functions platforms:

 - [AWS Lambda](https://aws.amazon.com/lambda/)
 - [Azure Functions](https://azure.microsoft.com/Functions/Serverless)
 - [Google Cloud Functions](https://cloud.google.com/functions/) 

## Languages

The sample functions in this repository have been written in the following software languages:

- Node.js
- Python
- Java

## Sample Functions

This GitHub repository contains sample functions you can use to build your own cloud functions. We have included sample functions to fetch data from the following data sources:

- [Elastic search server](https://github.com/fivetran/functions/tree/master/elastic_search)
- [Databases](https://github.com/fivetran/functions/tree/master/database)
- [APIs](https://github.com/fivetran/functions/tree/master/api/)
- [Files (such as CSV, TSV, and JSON)](https://github.com/fivetran/functions/tree/master/file)
- [London Tube (Transport API)](https://github.com/fivetran/functions/tree/master/LondonSubway)

## Demo

[See an overview of how Fivetran's cloud function connector work and a recorded demo of the Twitter function](https://www.youtube.com/watch?v=HrOdDKOPqhg).

## Resources

Learn more about Fivetran in [our documentation](https://fivetran.com/docs/getting-started).

Check out [Fivetran's blog](https://fivetran.com/blog).

Contact [our support team](https://support.fivetran.com/hc/en-us) for assistance and information. 

## License

See [Fivetran's license](https://github.com/fivetran/functions/blob/master/LICENSE).

## Contribution

Additional contributions to this repository are very welcome! Please create issues or open PRs against master.
