import os
import boto3

AWS_REGION = os.getenv("AWS_REGION") 
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID") 
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")  

# s3 = boto3.client('s3', region_name=AWS_REGION, aws_access_key_id=AWS_ACCESS_KEY_ID,
#                           aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

s3 = boto3.client('s3', region_name="ap-southeast-1", aws_access_key_id="AKIA3FLDZ5P3PVPJVCF6",
                          aws_secret_access_key="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")

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