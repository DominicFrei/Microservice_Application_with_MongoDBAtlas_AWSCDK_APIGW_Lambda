import json
import logging
import os

import boto3
from pymongo import MongoClient

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info('Received event: {}'.format(json.dumps(event)))

    # Check if the request body is present
    if 'body' not in event or event['body'] is None:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Request body is missing or empty'}),
            'headers': {'Content-Type': 'application/json'}
        }

    try:
        # Load the JSON object from the request body
        request_body = json.loads(event['body'])
    except Exception as e:
        logger.error('Error loading JSON from request body: {}'.format(e))
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid JSON in request body'}),
            'headers': {'Content-Type': 'application/json'}
        }

    # Retrieve the connection string from Secrets Manager
    secrets_manager = boto3.client('secretsmanager')
    secret_name = os.environ['ATLAS_URI']
    secret_value_response = secrets_manager.get_secret_value(SecretId=secret_name)
    connection_string = secret_value_response['SecretString']

    # Connect to MongoDB
    mongo_client = MongoClient(host=connection_string)
    app_database = mongo_client["app"]
    todos_collection = app_database["todos"]

    # Parse the request body to extract todo data
    request_body = json.loads(event['body'])
    todo_text = request_body['text']

    # Create a new todo document
    todo = {
        "text": todo_text
    }

    # Insert the todo document into the collection
    result = todos_collection.insert_one(todo)

    # Check if the todo was successfully inserted
    if result.inserted_id:
        # Return success response with the inserted todo ID
        response = {
            "statusCode": 201,
            "body": json.dumps({"id": str(result.inserted_id)}),
            "headers": {"Content-Type": "application/json"}
        }
    else:
        # Return error response if the insertion failed
        response = {
            "statusCode": 500,
            "body": "Failed to create todo",
            "headers": {"Content-Type": "application/json"}
        }

    return response
