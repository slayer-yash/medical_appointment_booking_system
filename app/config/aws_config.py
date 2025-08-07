import boto3
from app.config.config import ACCESS_KEY, SECRET_ACCESS_KEY

#boto3 initialization to access aws s3 bucket
s3 = boto3.client(
            "s3",
            aws_access_key_id = ACCESS_KEY,
            aws_secret_access_key = SECRET_ACCESS_KEY,
            region_name = "eu-north-1"
        )

bucket_name = "yash-jogi-prescription-bkt"