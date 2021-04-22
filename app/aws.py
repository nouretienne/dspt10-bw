import os
import dotenv
import boto3
from fastapi import APIRouter
import pandas as pd

router = APIRouter()

dotenv.load_dotenv(dotenv.find_dotenv())
aws_access_key = os.getenv('AWS_ACCESS_KEY')
aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
region = os.getenv('AWS_DEFAULT_REGION')
name = 's3'
s3 = boto3.resource(service_name=name, region_name=region, aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_access_key)


def getbucketname():
    bucket_name = []
    for bucket in s3.buckets.all():
        bucket_name.append(bucket.name)
    return bucket_name


def getbucketdata(bucket_name):
    bucket_data = []
    for obj in s3.Bucket(bucket_name).objects.all():
        bucket_data.append(obj)
    return str(bucket_data)


def objtojson(bucket_name, bucket_obj):
    obj = s3.Bucket(bucket_name).Object(bucket_obj).get()
    df = pd.read_csv(obj['Body'], index_col=0)
    df = df.reset_index(drop=True)
    df = df.to_json()
    return df


@router.get('/aws/bucket_name')
async def bucketname():
    bucket_name = getbucketname()
    return {'bucket-name': bucket_name}


@router.get('/aws/bucket_objects')
async def bucketdata(bucket_name: str):
    bucket_data = getbucketdata(bucket_name)
    return {'bucket-data': bucket_data}


@router.get('/aws/tojson')
async def tojson(bucket_name: str, bucket_obj: str):
    bucket_df = objtojson(bucket_name, bucket_obj)
    return bucket_df
