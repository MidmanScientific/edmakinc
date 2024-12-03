import boto3
from botocore.exceptions import ClientError
from decouple import config

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY =config("AWS_SECRET_ACCESS_KEY")
AWS_S3_REGION_NAME = config("AWS_S3_REGION_NAME")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")

def generate_presigned_url(object_key, expiration=20):
    """
    Generate a pre-signed URL to access an S3 object.
    :param object_key: The S3 key for the file.
    :param expiration: Time in seconds for the URL to remain valid.
    :return: Pre-signed URL as a string or None if error occurs.
    """
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION_NAME
    )
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': AWS_STORAGE_BUCKET_NAME, 'Key': object_key},
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        print(f"Error generating pre-signed URL: {e}")
        return None
