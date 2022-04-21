import json
import boto3

s3 = boto3.client("s3")

def lambda_handler(event, context):
    # TODO implement
    bucket_name = "job-app-data-bucket"
    
    fileName = 'tester' + '.json'
    s3_path = 'testraw/' + fileName
    
    # the json file to write
    myFile = {}
    myFile['ID'] = '123456'
    myFile['body'] = 'Bibop ich bin ein text'
    myFile['value'] = 500
    
    bytestream = bytes(json.dumps(myFile).encode("utf-8"))
    
    s3.put_object(Bucket=bucket_name, Key=s3_path, Body=bytestream)

    print('Put Complete walla')
