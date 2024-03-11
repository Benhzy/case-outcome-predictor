import os
import boto3

AWS_REGION = os.environ.get("AWS_REGION")
AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")

s3 = boto3.client('s3', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
bucket = 'sg-auth-bucket'
os.makedirs('data/raw', exist_ok=True)

def case_upload():
    folder_path = 'raw-cases'
    for filename in os.listdir(folder_path):
        s3.download_file(bucket, filename, f"{folder_path}/{filename}")

def case_download():
    objects = s3.list_objects_v2(Bucket = bucket)
    for obj in objects['Contents']:
        s3.download_file(bucket, obj['Key'], f"data/raw/{obj['Key']}")


# Uncomment the following lines to upload to/download from s3
#case_upload()
case_download()