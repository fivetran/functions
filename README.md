# Fivetran

[Fivetran](https://fivetran.com/) helps you centralize data from disparate sources into your data storage platform that you can manage directly from your browser. Fivetran’s fully automated connectors extract your data from cloud applications, databases, event logs, and more, and load it into your preferred data storage platform.

## Getting Started

[Create you Fivetran account](https://fivetran.com/signup?email=) and get started.

## Cloud Function Connectors

[Functions connectors](https://fivetran.com/docs/functions) allows you to code a custom data connector as an extension of Fivetran. If you have a custom data source or a private API that we don't support, you can develop a serverless ELT data pipeline using our Function connectors.

## Supported Platforms

Fivetran supports the following cloud functions platforms:

 - [AWS Lambda](https://aws.amazon.com/lambda/)
 - [Azure Functions](https://azure.microsoft.com/Functions/Serverless)
 - [Google Cloud Functions](https://cloud.google.com/functions/) 

## Sample Functions

The GitHub repo contains sample functions you can use to build your own cloud functions. We have included sample functions to fetch data from the following data sources:

- [Elastic search server](https://github.com/fivetran/functions/tree/master/elastic_search)
- [Databases](https://github.com/fivetran/functions/tree/master/database)
- [APIs](https://github.com/fivetran/functions/tree/master/api/)
- [Files (such as CSV, TSV, and JSON)](https://github.com/fivetran/functions/tree/master/file)
- [London Tube (Transport API)](https://github.com/fivetran/functions/tree/master/LondonSubway)

## Demo

See an overview of how these functions work and a [live demo of the Twitter function](https://www.youtube.com/watch?v=HrOdDKOPqhg).

## Support and Documentation 

Contact [our support team](https://support.fivetran.com/hc/en-us) if you need assitance.

Read more about Fivetran in [our documentation](https://fivetran.com/docs/getting-started).

## License

See [Fivetran's license information](https://github.com/fivetran/functions/blob/master/LICENSE).
