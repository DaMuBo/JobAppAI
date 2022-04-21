"""
Development part of the lambda function for the api calls 
from the Arbeitsagentur API

"""

import json
import boto3
import requests
import base64
def get_jwt():
    """fetch the jwt token object"""
    headers = {
        'User-Agent': 'Jobsuche/2.9.2 (de.arbeitsagentur.jobboerse; build:1077; iOS 15.1.0) Alamofire/5.4.4',
        'Host': 'rest.arbeitsagentur.de',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    }

    data = {
      'client_id': 'c003a37f-024f-462a-b36d-b001be4cd24a',
      'client_secret': '32a39620-32b3-4307-9aa1-511e3d7f48a8',
      'grant_type': 'client_credentials'
    }

    response = requests.post('https://rest.arbeitsagentur.de/oauth/gettoken_cc', headers=headers, data=data, verify=False)

    return response.json()

def search(jwt, what):
    """search for jobs. params can be found here: https://jobsuche.api.bund.dev/"""
    """
    **** TODO ****
        Hier die Funktion anpassen -> page als Input hinzunehmen, im aufruf dann ein umgang mit fehlermeldungen einbauen
    """
    params = (
        ('angebotsart', '1'),
        ('page', '2'),
        ('pav', 'false'),
        ('size', '100'),
        ('umkreis', '25'),
        ('was', what),
    )

    headers = {
        'User-Agent': 'Jobsuche/2.9.2 (de.arbeitsagentur.jobboerse; build:1077; iOS 15.1.0) Alamofire/5.4.4',
        'Host': 'rest.arbeitsagentur.de',
        'OAuthAccessToken': jwt,
        'Connection': 'keep-alive',
    }

    response = requests.get('https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v4/app/jobs',
                            headers=headers, params=params, verify=False)
    return response.json()


def job_details(jwt, job_ref):

    headers = {
        'User-Agent': 'Jobsuche/2.9.3 (de.arbeitsagentur.jobboerse; build:1078; iOS 15.1.0) Alamofire/5.4.4',
        'Host': 'rest.arbeitsagentur.de',
        'OAuthAccessToken': jwt,
        'Connection': 'keep-alive',
    }

    response = requests.get(
        f'https://rest.arbeitsagentur.de/jobboerse/jobsuche-service/pc/v2/jobdetails/{(base64.b64encode(job_ref.encode())).decode("UTF-8")}',
        headers=headers, verify=False)

    return response.json()


def job_rotator():
    """
    **** TODO ***** 
        hier eine while schleife so lanee wir neue seiten haben und es keinen fehler gibt
    """
    
    jwt = get_jwt()
    result = search(jwt["access_token"], "data science")
    
    """ 
    **** TODO ***** 
        alle daten zusammen fügen
    """ 
    print(result['stellenangebote'][0]["refnr"])
    print(job_details(jwt["access_token"], result['stellenangebote'][0]["refnr"]))
    
    """
    **** TODO *****
        return der zusammengefügten Daten
        Im Lambdahandler dann eine For schleife bauen die die Json files wegspeichert
    """

def lambda_handler(event, context):
    # TODO implement
    s3 = boto3.client("s3")
    
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
