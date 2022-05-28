"""
Die Funktion lädt die stellenbeschreibungen aus der DynamoDB, erzeugt die manifest datei und speichert das im S3 Bucket

"""
import json
from datetime import datetime
import boto3
from boto3.dynamodb.conditions import Key

def query_job_data(datum, dynamodb):
    """
    using query method to get requested data based on the partition key which is the veroeffentlichungsdatum
    """

    table = dynamodb.Table('JobData')
    response = table.query(
        KeyConditionExpression=Key('aktuelleVeroeffentlichungsdatum').eq(datum),
    )
    return response['Items']


def lambda_handler(event, context):
    """
    Function um von dynamo DB die benötigten Datensets zu laden und eine Manifest Datei zu erzeugen
    """
    dynamodb = boto3.resource('dynamodb')
    s3 = boto3.resource("s3")

    datobj = datetime.now()
    datum =  str(datobj.year) + '-' + str(datobj.month).zfill(2) + '-' + str(datobj.day).zfill(2)

    bucket_name = 'job-app-data-bucket'
    filename = "mymanifest.jsonl"

    response = query_job_data(datum, dynamodb)
    s3_path = 'manifest/' +filename
    with open('/tmp/output.jsonl', 'w') as outfile:
        for row in response:
            if 'stellenbeschreibung' in row.keys():
                mydict = {'source':row['stellenbeschreibung']}
                json.dump(mydict, outfile)
                outfile.write('\n')

    s3.meta.client.upload_file('/tmp/output.jsonl', bucket_name, s3_path)
    print('Created Manifest Successfull')
