import json
import boto3
import re
import logging
import eventnotifier
import os
import datetime
from dateutil.tz import tzutc

HOOK_URL = os.environ['HookUrl']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    sns_message = json.loads(event['Records'][0]['Sns']['Message'])
    source_bucket = sns_message["source_bucket"]
    source_root = sns_message["source_root"]
    target_bucket = sns_message["target_bucket"]
    target_root = sns_message["target_root"]
    archive_bucket = sns_message["archive_bucket"]
    archive_root = sns_message["archive_root"]

    client = boto3.client('s3')

    s3_objects = client.list_objects(
        Bucket=source_bucket,
        Prefix=source_root
    )

    if not s3_objects.get('Contents'):

        message = 'No files found in s3://{}/{}'.format(source_bucket, source_root)
        eventnotifier.invoke_notification(HOOK_URL, logger, "Error: List Objects Operation Failed", message)
        
        return {
            "statusCode": 400,
            "body": json.dumps({
                "message": message,
            }),
        }

    for s3_obj in s3_objects['Contents']:
        object_key = s3_obj['Key']
        last_modified = s3_obj['LastModified']

        event_date = '{}/{}/{}'.format(last_modified.year, last_modified.month, last_modified.day)
        
        # Pull out the file name and prefix with the date of the triggered S3 notification 
        key_name = object_key.replace('temp/', '')
        
        key_components = key_name.split('/')
        file_name = key_components.pop(-1)
        key_components.pop(0)
        file_path = '/'.join(key_components)

        # Set the new full file path name
        full_key_name = "{}/{}/{}".format(file_path, event_date, file_name)
        # Move to target_bucket
        key = '{}/{}'.format(target_root, full_key_name)
        logging.info("Starting copy operation of {0} to {1}.".format(object_key, key))

        try:
            client.copy_object(
                    Bucket=target_bucket,
                    CopySource={
                        'Bucket': source_bucket,
                        'Key': object_key
                    },
                    Key=key
                )
            logging.info("Finished copy operation of {0} to {1}.".format(object_key, key))
        except Exception as e:
            logging.error('{} KEY: {}'.format(e, key))
            eventnotifier.invoke_notification(HOOK_URL, logger, "Error: Copy Object Operation Failed", (e, 'Key: '+ key))

            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": '{} KEY: {}'.format(e, key),
                }),
            }

        # Move to archive_bucket
        key = '{}/{}'.format(archive_root, full_key_name)
        logging.info("Starting copy operation of {0} to {1}.".format(object_key, key))

        try:
            client.copy_object(
                    Bucket=archive_bucket,
                    CopySource={
                        'Bucket': source_bucket,
                        'Key': object_key
                    },
                    Key=key
                )
            logging.info("Finished copy operation of {0} to {1}.".format(object_key, key))
        except Exception as e:
            logging.error('{} KEY: {}'.format(e, key))
            eventnotifier.invoke_notification(HOOK_URL, logger, "Error: Copy Object Operation Failed", (e, 'Key: '+ key))

            return {
                "statusCode": 400,
                "body": json.dumps({
                    "message": '{} KEY: {}'.format(e, key),
                }),
            }
    
    # Delete the files that have been moved
    for s3_obj in s3_objects['Contents']:

        client.delete_object(
            Bucket=source_bucket,
            Key=s3_obj['Key']
        )

        logging.info("Deleted {}".format(s3_obj['Key']))

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "File movement operations completed successfully.",
        }),
    }