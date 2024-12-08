import boto3
import json
import os
import logging
from tika import parser
from io import BytesIO

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info('********************** Environment and Event variables are *********************')
    logger.info(os.environ)
    logger.info(event)
    extract_content(event)

    return {
        'statusCode': 200,
        'body': json.dumps('Execution is now complete')
    }

def extract_content(event):
    try:
        targetBucket = os.environ['TARGET_BUCKET']
    except:
        targetBucket = "gl-inter-store-esanchez"
    print('Target bucket is', targetBucket)

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    print('The s3 bucket is', bucket, 'and the file name is', key)
    
    s3client = boto3.client('s3')
    response = s3client.get_object(Bucket=bucket, Key=key)
    pdf_content = response["Body"].read()

    # Parse PDF with Tika
    parsed = parser.from_buffer(pdf_content)
    
    # Extract metadata and content
    metadata = parsed.get("metadata", {})
    content = parsed.get("content", "No content found")
    
    # Format the output
    output = f"""Title: {metadata.get('title', 'N/A')}
Author: {metadata.get('Author', 'N/A')}
Creation Date: {metadata.get('Creation-Date', 'N/A')}
Content:
{content}"""
    
    print("Extracted text: ", content[:200] + "...") # Log first 200 chars of content
    print("Metadata: ", metadata)
    
    # Save to target bucket
    s3client.put_object(
        Bucket=targetBucket,
        Key=f"{key}.txt",
        Body=output
    )

    print('All done, returning from extract content method')