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
import boto3
import spacy

def get_data():
    """
    Hole daten aus der dynamo DB nach dem beschriebenen muster und gib diese zurück
    """
    
    
def write_data():
    """
    Aktualisiere die Daten mit den angereicherten Skills in der dynamoDB
    """
    
def calculate_skills():
    """
    Extrahiere die skills aus den Texten und gib diese für jeden fall entsprechend zurück
    Wenn keine skills gefunden wurden gib eine leere liste zurück
    """

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
                    os.makedirs(os.path.dirname(local + os.sep + file.get('Key') + os.sep ))
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
    bucket_name =  "job-app-data-bucket"
    object_key = 'models/skill_ner_model'  # replace object key
    if (os.path.isdir("/tmp/" + object_key)==False):
        download_dir(client, resource, object_key, '/tmp',bucket_name)
        print(os.path.isdir("/tmp/" + object_key))
    
    #nlp = spacy.load('/tmp/' + object_key)
    # hier text reinladen
    #text = "Hallo ich bin ein test text. Bittee sag mir ob ich ok bin und ob ich python oder R kann."
    #oc = nlp(text)
    #print(oc)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
