# TODO:
#


# FIXME:

import json
import os

import boto3
import pandas as pd

bucket_name = "job-app-data-bucket"
labeling_files = [
    "manifest_output/job-app-labeling/manifests/output/output.manifest",
    "manifest_output/job-app-labeling/manifests/intermediate/1/output.manifest",
    "manifest_output/job-app-labeling-2/labelingJob3/manifests/intermediate/1/output.manifest",
]
output_files = [
    "labeling_job_1_output.manifest",
    "labeling_job_1_intermediate_output.manifest",
    "labeling_job_2_intermediate_output.manifest",
]


s3 = boto3.client("s3")

PROJECT_ROOT_DIR = "."
data_path = os.path.join(PROJECT_ROOT_DIR, "data")
os.makedirs(data_path, exist_ok=True)


def get_data():

    # alle Dateien holen und ablegen
    for index, labeling_file in enumerate(labeling_files):
        print(f"{labeling_file}")
        output_file = output_files[index]
        output_path = os.path.join(data_path, output_file)

        s3.download_file(
            Bucket=bucket_name,
            Key=labeling_file,
            Filename=output_path,
        )

        print(f"{output_file} saved")


def manifest_to_json(manifest_file):

    print(f"{manifest_file} to JSON")
    encoding = "utf-8"
    manifest_path = os.path.join(data_path, manifest_file)
    file = open(manifest_path, "r", encoding=encoding)

    # print(manifest_path)

    json_folder_name = manifest_file.replace(".manifest", "")
    json_folder = os.path.join(data_path, json_folder_name)
    os.makedirs(json_folder, exist_ok=True)

    for index, line in enumerate(
        file
    ):  # jede Line im Manifest ist ein eigenes JSON

        json_file_name = json_folder_name + "_" + str(index) + ".json"
        json_file_path = os.path.join(json_folder, json_file_name)
        with open(json_file_path, "w", encoding=encoding) as f:
            json.dump(json.loads(line), f, indent=4)
    print(f"{manifest_file} to JSON done")


get_data()
for file in output_files:
    manifest_to_json(file)
