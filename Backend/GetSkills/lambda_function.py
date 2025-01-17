"""
Developing the lambda function for getting the data from the dynamodb
"""

import base64
import json
import re
from datetime import datetime
from datetime import timedelta
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
        ProjectionExpression='skills,titel'
    )
    return response['Items']

def lambda_handler(event, context):
    """
    Function um von dynamo DB die benötigten Datensets zu laden und in json format an die API zurück zu liefern.
    """
    dynamodb = boto3.resource('dynamodb')
    dynclient = boto3.client('dynamodb')
    
    if event['timeframe'] == '':
        timeframe = 0
    else:
        timeframe = int(event['timeframe'])
        
    jobs = event['jobs']
    datobj = get_min_datum(timeframe)
    numbjobs = 0
    dicskills = {}
    while datobj <= datetime.now():
        datum =  str(datobj.year) + '-' + str(datobj.month).zfill(2) + '-' + str(datobj.day).zfill(2)
        datobj = datobj + timedelta(days=1)
        response = query_job_data(datum,dynamodb)
        for row in response:
            if 'skills' in row.keys():
                if jobs == '':
                    numbjobs += 1
                    for skill in row['skills']:
                        if skill.lower() in dicskills.keys():
                            dicskills[skill.lower()] += 1
                        else:
                            dicskills[skill.lower()] = 1
                elif jobs.lower() in row['titel'].lower():
                    numbjobs += 1
                    for skill in row['skills']:
                        if skill.lower() in dicskills.keys():
                            dicskills[skill.lower()] += 1
                        else:
                            dicskills[skill.lower()] = 1


    for skill in dicskills.keys():
        dicskills[skill] = dicskills[skill] / numbjobs

    liste = sorted(dicskills,key= dicskills.get, reverse=True)
    output = {}
    for key in liste:
        output[key] = dicskills[key]

    return json.dumps({
        'statusCode': 200,
        'body': output
    })
