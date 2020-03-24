# cwl-to-firehose

## Automated CloudWatch Routing

Proof of Concept to show how CloudWatch Event Rules + Lambda can route cloudwatch logs to specific destinations via Kinesis Firehose.

## About

Some CloudWatch logs are more important than others.  You'll want to route these logs to destinations like Redshift or Splunk to get the most insight and value out of your logs.  To do this automatically, we can utilize cloudwatch event rules to route cloudwatch log groups any time a specific tag is added.

----

## Architecture

![Stack-Resources](https://github.com/CYarros10/csv-to-parquet-via-glue/blob/master/architecture/datalake-transforms.png)

----

## Deploying Cloudformation


1. Go to [AWS Cloudformation Console](https://console.aws.amazon.com/cloudformation/) and choose **Create stack**
2. upload the cloudformation/master.yml template
3. enter parameters

This Stack will create the following:

1. S3 bucket for logs destination
2. firehose delivery stream
3. CWL to Firehose roles/policies
4. lambda function
5. cloudwatch events rule

## Viewing Results

### Add a tag to a cloudwatch log group

Tag Basics

You use the AWS CLI or CloudWatch Logs API to complete the following tasks:

- Add tags to a log group when you create it
- Add tags to an existing log group
- List the tags for a log group
- Remove tags from a log group

You can use tags to categorize your log groups. For example, you can categorize them by purpose, owner, or environment. Because you define the key and value for each tag, you can create a custom set of categories to meet your specific needs. For example, you might define a set of tags that helps you track log groups by owner and associated application. Here are several examples of tags:

- Project: Project name
- Owner: Name
- Purpose: Load testing
- Application: Application name
- Environment: Production

via [Working with Log Groups and Log Streams](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/Working-with-log-groups-and-streams.html#log-group-tagging)

Examples:

        aws logs tag-log-group --log-group-name /aws-glue/crawlers --tags captured=true

### Check to see if subscription filter was added

1. Go to [CloudWatch Log groups Console])(https://console.aws.amazon.com/cloudwatch/home#logs:)
2. Your Log Group should now have a subscription under the **Subscriptions** column.

### See logs routed to firehose

Once your log group receives logs, they will be sent to the Kinesis Firehose Delivery Stream.

1. Use the [Kinesis Console](https://console.aws.amazon.com/kinesis/home) to select the newly created Kinesis Firehose delivery stream.
2. Select Monitoring tab to view events on the delivery stream.
3. Go to the [S3 Console](https://s3.console.aws.amazon.com/s3/home) and select the newly created S3 bucket. Logs should be delivered there.