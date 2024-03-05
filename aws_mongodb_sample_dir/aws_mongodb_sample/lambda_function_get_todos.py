import os

import boto3
from bson.json_util import dumps
from pymongo import MongoClient


def lambda_handler(event, context):
    secrets_manager = boto3.client('secretsmanager')
    secret_name = os.environ['ATLAS_URI']
    secret_value_response = secrets_manager.get_secret_value(SecretId=secret_name)
    connection_string = secret_value_response['SecretString']

    mongo_client = MongoClient(host=connection_string)
    app_database = mongo_client["app"]
    todos_collection = app_database["todos"]

    todos = todos_collection.find()

    todos_json = dumps(todos)

    if todos_json:
        response = {
            "statusCode": 200,
            "body": todos_json,
            "headers": {"Content-Type": "application/json"}
        }
        return response
    else:
        return {
            "statusCode": 404,
            "body": "No todos found",
            "headers": {"Content-Type": "application/json"}
        }
