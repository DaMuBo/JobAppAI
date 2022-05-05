from lambda_function import *
import json
import warnings
from pathlib import Path

def get_folder():
    """
    returns the actual project folder and makes it easy for file handlings
    """
    
    return Path.cwd()

if __name__ == '__main__':
    warnings.filterwarnings("ignore")
    
    pfad = get_folder() / 'raw'
    myList = job_rotator(None,'data')
    for row in myList:
        if 'refnr' in row.keys():
            myFile = row
            filename = row['refnr'].encode('unicode-escape')
            filename = filename.decode('ascii', errors='ignore').replace('\\','_').replace('/','_') + '.json'
            s3_path = pfad / filename

            with open(s3_path, 'w') as fp:
                json.dump(myFile, fp)
                
        if 'stellenbeschreibung' in row.keys():
            myFile = row['stellenbeschreibung'].replace('\n',' ')
            filename = row['refnr'].encode('unicode-escape')
            filename = filename.decode('ascii', errors='ignore').replace("\\",'_').replace('/','_') + '.txt'
            s3_path = 'unlabeled/' + filename
            try:    
                with open(s3_path, 'w', encoding='unicode-escape') as fp:
                    fp.write(myFile)
            except:
                print(myFile)
                raise