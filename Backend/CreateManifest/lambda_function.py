"""
Die Funktion lädt die stellenbeschreibungen aus der DynamoDB, erzeugt die manifest datei und speichert das im S3 Bucket


Funktionen:


"""

import json
import boto3
import base64


def lambda_handler(event, context):
    # TODO implement
    dynamodb = boto3.client("dynamodb")   
    
    limit = 0 # days since the writing for initial load = None After that = 0 or 1
    what = 'data' # what is searched for'
    
    # the json file to write
    myList = job_rotator(limit, what)
    for row in myList:
        if 'refnr' in row.keys():
            myItem = dict_to_item(row)
            dynamodb.put_item(TableName='JobData', Item=myItem)

    print('Put Complete Writing Data to Bucket')
