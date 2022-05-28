"""
Skill Extractor

Holt sich die Texte aus der Dynamo DB und extrahiert die skills aus den stellenbezeichnungen

Functions:
-------------------------------
lambda_handler:
    Main Function, Steuert die Eingaben und anderen Funktionen auf Basis des Inputs

extractor_rule:
    Extraction function: Regelbasierte Funktion zum extrahieren der daten
"""
import os
import json
import re
from datetime import datetime
from datetime import timedelta
import boto3
from boto3.dynamodb.conditions import Key
import spacy


def clean_text(text):
    """
    Bereinigung von möglichen Sonderzeichen
    """
    cleaned = re.sub(r"[\(\[].*?[\)\]]", "", text)
    return cleaned

def get_min_datum(timeframe=0):
    """
    Ermittelt das minum datum ausgehend von heute ()
    """
    datum = datetime.now()
    # ziehe die tage ab
    return datum - timedelta(days=timeframe)


def dict_to_item(raw):
    """
    takes a dictionary and is returning the datatype of each item in a format for writing it into a dynamoDB
    is using recursive calls on itself to get the informations out of lists and dicitonarys
    """
    if isinstance(raw,dict):
        resp = {}
        for k,v in raw.items():
            if isinstance(v,str):
                resp[k] = {
                    'S': v
                }

            elif isinstance(v,bool):
                resp[k] = {
                    'S': str(v)
                }
            elif isinstance(v,(int,float)):
                resp[k] = {
                    'N': str(v)
                }
            elif isinstance(v,dict):
                resp[k] = {
                    'M': dict_to_item(v)
                }
            elif isinstance(v,list):
                resp[k] = {"L":[]}
                for i in v:
                    if isinstance(i,dict):
                        resp[k]["L"].append({"M":dict_to_item(i)})
                    else:
                        resp[k]["L"].append(dict_to_item(i))
        return resp
    elif isinstance(raw,str):
        return {
            'S': raw
        }
    elif isinstance(raw,(int,float)):
        return {
            'N': str(raw)
        }
    return {
        'S':str(raw)
    }

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

def download_dir(client, resource, dist, local='/tmp', bucket='s3bucket'):
    """
    Kopiere das ml in einen lokalen ordner um für spacy verfügbar zu sein.
    """
    paginator = client.get_paginator('list_objects')
    page_iterator = paginator.paginate(Bucket=bucket, Prefix=dist)
    for result in page_iterator:
        if result.get('Contents') is not None:
            for file in result.get('Contents'):
                if not os.path.exists(os.path.dirname(local + os.sep + file.get('Key'))):
                    os.makedirs(os.path.dirname(local + os.sep + file.get('Key')))
                if file.get('Key') != dist + '/' :
                    if file.get('Size') != 0: # wenn das file size = 0 dann ist es ein directory und soll ignoriert werden
                        resource.meta.client.download_file(bucket, file.get('Key'), local + '/' + file.get('Key'))
                        


def lambda_handler(event, context):
    """
    Main Function zum ausführen der restlichen Codes und laden der benötigten Daten aus den Datenbanken
    Schreibt auch die Ergebnisse zurück in die DB
    """
    client = boto3.client('s3')
    resource = boto3.resource('s3')
    dynamodb = boto3.resource('dynamodb')
    dynclient = boto3.client('dynamodb')
    bucket_name =  "job-app-data-bucket"
    object_key = 'models/skill_ner_model'  # replace object key
    if (os.path.isdir("/tmp/" + object_key)==False):
        download_dir(client, resource, object_key, '/tmp',bucket_name)
    
    datobj = get_min_datum(1)
    nlp = spacy.load('/tmp/' + object_key)
    while datobj <= datetime.now():
        datum =  str(datobj.year) + '-' + str(datobj.month).zfill(2) + '-' + str(datobj.day).zfill(2)
        datobj = datobj + timedelta(days=1)
        response = query_job_data(datum,dynamodb)
        for row in response:
            if 'stellenbeschreibung' in row.keys():
                doc = nlp(clean_text(row['stellenbeschreibung']))
                if len(doc.ents) > 0:
                    row['skills'] = list(set([x.text for x in doc.ents]))
                    print(datum, row['skills'])
                    myitem = dict_to_item(row)
                    dynclient.put_item(TableName='JobData', Item=myitem)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
