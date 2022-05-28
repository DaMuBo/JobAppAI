"""
Developing the lambda function for getting the data from the dynamodb
"""

import base64
import json
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key

def get_min_datum(timeframe=0):
    """
    Ermittelt das minum datum ausgehend von heute ()
    """
    datum = datetime.now()
    # ziehe die tage ab
    return datum - timedelta(days=timeframe)


def query_job_data(datum, dynamodb):
    """
    Lade die Daten aus der DB
    """
    table = dynamodb.Table('JobData')
    response = table.query(
        KeyConditionExpression=Key('aktuelleVeroeffentlichungsdatum').eq(datum),
        #Limit = limit
    )
    return response['Items']

def lambda_handler(event, context):
    """
    Function um von dynamo DB die benötigten Datensets zu laden und in json format an die API zurück zu liefern.
    """
    dynamodb = boto3.resource('dynamodb')
    dynclient = boto3.client('dynamodb')
    
    return {
        
    }