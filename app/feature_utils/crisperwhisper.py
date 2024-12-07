import requests
import json
import boto3
import time
from dotenv import load_dotenv
import os
import re

load_dotenv()
aws_access_key_id = os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")
def get_upload_url(username):
    # Replace with your Lambda function's API Gateway endpoint
    url = "https://6tc6duce7g4vx27wa4ljnn4u2y0cssms.lambda-url.us-west-1.on.aws/"

    # Replace with the desired username value
    payload = {
        "username": username
    }


    # Send the POST request
    try:
        response = requests.post(url, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            response_json = response.json()
            # print("Response:", response.json())
            # Example input string
            input_string = response_json['message']

            # Regular expression to match the desired pattern
            pattern = r"TO_PROCESS/([^/]+/\d+)\.mp4"

            # Extract the match
            match = re.search(pattern, input_string)

            if match:
                result = match.group(1)  # Extract the username/numbers part
                # print("Extracted:", result)
            else:
                raise ValueError("File Name in unexpected Format.")


            return {"url": response_json['message'], "file": result}
        else:
            raise ValueError(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        print("An error occurred:", str(e))


def upload_video_to_presigned_url(presigned_url, video_file_path):
    with open(video_file_path, 'rb') as file:
        response = requests.put(presigned_url, data=file)

    if response.status_code == 200:
        print("Video uploaded successfully!")
    else:
        print("Error uploading video:", response.status_code, response.text)




def get_transcript(file, timeout=360, wait_interval=5, bucket_name = 'mids-capstone-aceinterview', folder_name = 'CrisperWhisperEndpoint'):
    """
    Fetch a JSON file representing the transcript with word level timestamps from an S3 bucket, waiting for it to appear if necessary.

    Args:
        file (str): Name of the JSON file to fetch without the .json extension.
        timeout (int): Maximum time to wait (in seconds) for the file to appear.
        wait_interval (int): Time to wait (in seconds) between retries.
        bucket_name (str): Name of the S3 bucket.
        folder_name (str): Name of the folder in the bucket.

    Returns:
        dict: Parsed JSON content if the file is found.

    Raises:
        FileNotFoundError: If the file does not appear within the timeout period.
        ValueError: If the file content is not valid JSON.
    """
    # Initialize the S3 client
    s3_client = boto3.client('s3', aws_access_key_id = aws_access_key_id, aws_secret_access_key = aws_secret_access_key)

    # Construct the key (path to the file in the bucket)
    key = f"{folder_name}/{file}.json"

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            # Attempt to fetch the file
            response = s3_client.get_object(Bucket=bucket_name, Key=key)
            # Read and parse the JSON content
            content = json.loads(response['Body'].read())
            json_data = json.loads(content)

            return json_data

        # except s3_client.exceptions.NoSuchKey:
        #     print(f"File '{key}' not found. Retrying in {wait_interval} seconds...")
        #     time.sleep(wait_interval)  # Wait before retrying
        #
        # except json.JSONDecodeError as e:
        #     raise ValueError(f"Error decoding JSON from file '{key}': {e}")

        except Exception as e:
            time.sleep(wait_interval)  # Wait before retrying
            #raise Exception(f"An unexpected error occurred: {e}")

    # If we exit the loop, the file was not found within the timeout period
    raise FileNotFoundError(f"File '{key}' not found in bucket '{bucket_name}' after {timeout} seconds.")
