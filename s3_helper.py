import os
import boto3

AWS_REGION = os.environ.get("AWS_REGION")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

client = boto3.client('s3', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
s3 = boto3.resource("s3")
bucket = s3.Bucket('sg-auth-bucket')

def case_upload():
    folder_path = 'raw-cases'
    for filename in os.listdir(folder_path):
        bucket.download_file(filename, f"{folder_path}/{filename}")

def case_download():
    objects = s3.list_objects_v2(Bucket=bucket)
    for obj in objects['Contents']:
        bucket.download_file(obj['Key'], f"raw-cases/{obj['Key']}")