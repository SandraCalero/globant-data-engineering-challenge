import boto3
import logging
import os
from typing import List
from botocore.exceptions import NoCredentialsError, ClientError


def read_s3_files(bucket_name: str, prefix: str = "") -> List[dict]:
    """Reads files from an S3 bucket and returns a list with content"""
    logging.info(f"Starting file reading from bucket: {bucket_name}, prefix: {prefix}")
    
    try:
        # Try to use AWS CLI credentials
        s3 = boto3.client('s3')
        logging.info("S3 client created successfully")
        
        # List objects
        logging.info("Listing objects in S3...")
        response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        files_data = []
        
        if 'Contents' in response:
            logging.info(f"Found {len(response['Contents'])} files to process")
            for obj in response['Contents']:
                key = obj['Key']
                size = obj['Size']
                logging.info(f"Processing file: {key} (size: {size} bytes)")
                
                # Read file content
                file_obj = s3.get_object(Bucket=bucket_name, Key=key)
                content = file_obj['Body'].read().decode('utf-8')
                logging.info(f"File {key} read successfully, content: {len(content)} characters")
                
                files_data.append({
                    'key': key,
                    'content': content,
                    'size': size
                })
        else:
            logging.warning(f"No files found in bucket {bucket_name} with prefix {prefix}")
        
        logging.info(f"Processing completed. Total files processed: {len(files_data)}")
        return files_data
        
    except NoCredentialsError:
        error_msg = """
        AWS credentials not found. 
        
        Solutions:
        1. Verify AWS CLI is configured: aws configure list
        2. Configure credentials: aws configure
        3. Or use environment variables: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
        """
        logging.error(error_msg)
        raise Exception(error_msg)
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NoSuchBucket':
            raise Exception(f"Bucket '{bucket_name}' does not exist or you don't have permissions to access it.")
        elif error_code == 'AccessDenied':
            raise Exception(f"Access denied to bucket '{bucket_name}'. Verify your permissions.")
        else:
            raise Exception(f"AWS Error: {error_code} - {e.response['Error']['Message']}")
            
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise Exception(f"Unexpected error: {str(e)}")