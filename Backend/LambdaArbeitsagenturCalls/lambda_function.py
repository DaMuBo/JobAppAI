"""
Development part of the lambda function for the api calls
from the Arbeitsagentur API

funktionen:
    get_jwt(): Holt das Access Token zur Authentifizierung bei der API

    search(): Führt die Suche aus und gibt die Referenznr in einer Liste zurück mit welcher die Jobbeschreibungen gefunden werden können

    job_details(): Holt die Jobdetail Informationen für einen konkreten Job aus der API

    job_rotator(): kombiniert die Funktionen get_jwt, search und job_details. Außerdem werden die Ergebnisse in einer Liste gesammelt
        und zurückgegeben

    lambda_handler:
        definiert rahmenbedingungen und führt den job_rotator() aus. Die Ergebnisse werden unter ihrer refnr im S3 Bucket gespeichert.
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

def search(jwt, what, page, limit):
    """search for jobs. params can be found here: https://jobsuche.api.bund.dev/
    Inputs:
    --------------------------------------

    jwt:
        Das Access Token für den Zugriff

    what: 
        Der Suchbergriff nach dem gesucht wird

    page:
        Die Seite die aufgesucht werden soll

    limit:
        Wenn nicht None dann wird eine Info mit veroeffentlichseit an parameter angehängt zur Eingrenzung

    """

    params = (
        ('angebotsart', '1'),
        ('page', page),
        ('pav', 'false'),
        ('size', '100'),
        ('was', what),
    )
    if limit is not None:
        params = params + (
            ('veroeffentlichtseit', limit),
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
    """
    Holt die Detaildaten zu einem Job aus der API
    """

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


def job_rotator(limit=None, what='data'):
    """
    Input:
    
        limit: Integer/None
            wenn nicht None dann gibt es die maximale Anzahl an Tage in die Vergangenheit an.
    """
    checker = True
    page = 1
    myList = []
    
    while(checker==True):
        jwt = get_jwt()
        result = search(jwt["access_token"], what, page, limit)
        if 'stellenangebote' in result.keys():
            for row in result['stellenangebote']:
                output = job_details(jwt["access_token"], row["refnr"])
                myList.append(output)
            page += 1
        else:
            checker=False
    
    return myList
        

def dict_to_item(raw):
    """
    takes a dictionary and is returning the datatype of each item in a format for writing it into a dynamoDB
    is using recursive calls on itself to get the informations out of lists and dicitonarys
    
    """
    if type(raw) is dict:
        resp = {}
        for k,v in raw.items():
            if type(v) is str:
                resp[k] = {
                    'S': v
                }
            elif type(v) is int:
                resp[k] = {
                    'I': str(v)
                }
            elif type(v) is dict:
                resp[k] = {
                    'M': dict_to_item(v)
                }
            elif type(v) is list:
                resp[k] = []
                for i in v:
                    resp[k].append(dict_to_item(i))
                    
        return resp
    elif type(raw) is str:
        return {
            'S': raw
        }
    elif type(raw) is int:
        return {
            'I': str(raw)
        }


def lambda_handler(event, context):
    """
    Finale Funktion die von Lambda aufgerufen wird und die Daten ausführt
    """
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
