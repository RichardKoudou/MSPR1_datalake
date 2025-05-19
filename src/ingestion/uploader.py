import os
import boto3

def upload_folder_to_s3(local_folder, bucket_name, s3_prefix, aws_cfg):
    print(f"Upload des fichiers vers s3://{bucket_name}/{s3_prefix}/")

    session = boto3.Session(
        aws_access_key_id=aws_cfg["access_key"],
        aws_secret_access_key=aws_cfg["secret_access_key"],
        region_name=aws_cfg.get("region", "eu-west-1")
    )
    s3 = session.client("s3")

    for root, _, files in os.walk(local_folder):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_folder)
            s3_key = os.path.join(s3_prefix, relative_path).replace("\\", "/")

            print(f"Upload {file} vers s3://{bucket_name}/{s3_key}")
            s3.upload_file(local_path, bucket_name, s3_key)
