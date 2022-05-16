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
import json

def extractor_rule(text):
    """
    Regelbasierte Extraction von Skills
    Input:
    ----------------
    text: string,
        Text aus dem die Skills extrahiert werden sollen

    output:
    ------------
    return skills: liste
        liste mit den gefundenen Skilsl in dem Text
    """
    skills = []
    liste = ['python','sql','node.js','angular','aws','gcp','azure']
    for skill in liste:
        if skill in text.lower():
            skills.append(skill)

    return skills


def lambda_handler(event, context):
    """
    Main Function zum ausführen der restlichen Codes und laden der benötigten Daten aus den Datenbanken
    Schreibt auch die Ergebnisse zurück in die DB
    """
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
