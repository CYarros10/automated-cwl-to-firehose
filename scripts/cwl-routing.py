import json
import boto3
import os

# initiate boto3 logs client
session = boto3.session.Session()
logs_client = session.client('logs')

# retrieve environment variables
sub_filter_pattern=""
sub_filter_name= str(os.getenv('SUB_FILTER_NAME'))
firehose_destination_arn = str(os.getenv('SUB_FIREHOSE_DEST_ARN'))
cloudwatch_to_firehose_role_arn = str(os.getenv('SUB_ROLE_ARN'))
tag_key = str(os.getenv('TAG_KEY'))
tag_value = str(os.getenv('TAG_VALUE'))

def lambda_handler(event, context):

    print("Beginning Lambda Execution...")

    resource_type = get_resource_type(event)

    # check to see if event resource type is log-group
    if(get_resource_type(event) == 'log-group'):

        # get log group name
        log_group_name = get_log_group_name(event)

        # retrieve log group tags
        tags = get_log_group_tags(event)

        # check to see if there is a tag match
        if (tag_key in tags.keys()):

            tag_value_found = str(tags[tag_key]).lower()

            # tag match found. determine if key value is correct
            if (tag_value_found == tag_value):
                try:
                    # put subscription filter on the log group. (route logging to a kinesis delivery stream)
                    response_put_subscription_filter = logs_client.put_subscription_filter(
                        logGroupName=log_group_name,
                        filterName=sub_filter_name,
                        filterPattern=sub_filter_pattern,
                        destinationArn=firehose_destination_arn,
                        roleArn=cloudwatch_to_firehose_role_arn,
                        distribution='Random'
                    )

                    # check to see if subscription filter successfully added and destination is correct
                    if (get_log_group_subscription(log_group_name, sub_filter_name)['subscriptionFilters'][0]['destinationArn'] == firehose_destination_arn):
                        print("success. cloudwatch log group [" + log_group_name + "] is routed to firehose destination: "+firehose_destination_arn)
                except Exception as e:
                    print(str(e))

            # if tag is not true, we want to remove the subscription filter
            else:
                if (len(get_log_group_subscription(log_group_name, sub_filter_name)['subscriptionFilters']) != 0):
                    try:
                        response_delete_subscription_filter = logs_client.delete_subscription_filter(
                            logGroupName=log_group_name,
                            filterName=sub_filter_name
                        )
                        print("success. cloudwatch log group [" + log_group_name + "] is no longer routed to firehose destination: "+firehose_destination_arn)
                    except Exception as e:
                        print(str(e))
                else:
                    print("cloudwatch log group [" + log_group_name + "] has no subscription filter / destination.")
        else:
            print("failed. tag key not found.")
    else:
        print("failed. resource-type was not log-group.")

    print("Ending Lambda Execution...")

def get_resource_type(event):
    raw_cloudwatch_msg = event
    resource_type = raw_cloudwatch_msg['detail']['resource-type']
    return resource_type

def get_log_group_name(event):
    raw_cloudwatch_msg = event
    log_group_arn = raw_cloudwatch_msg['resources'][0]
    log_group_name = log_group_arn.split("log-group:",1)[1]
    return log_group_name

def get_log_group_tags(event):
    raw_cloudwatch_msg = event
    log_group_tags = raw_cloudwatch_msg['detail']['tags']
    return log_group_tags

def get_log_group_subscription(log_group_name, sub_filter_name):
    response_describe_subscription_filters = logs_client.describe_subscription_filters(
        logGroupName=log_group_name,
        filterNamePrefix=sub_filter_name,
        limit=1
    )
    return response_describe_subscription_filters