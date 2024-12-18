import requests
import json
import boto3
import time
from dotenv import load_dotenv
import os
import re
import asyncio

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




async def get_transcript(file, timeout=360, wait_interval=5, bucket_name = 'mids-capstone-aceinterview', folder_name = 'CrisperWhisperEndpoint'):
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
    url = "https://ye76kypj5yv3wof2jq55mi7ffu0clmww.lambda-url.us-west-1.on.aws/"

    # Replace with the desired username value
    payload = {
        "file": file
    }
    try:
        response = requests.post(url, json=payload, timeout=None)
        # Check if the request was successful
        if response.status_code == 200:
            response_json = response.json()
            return response_json
        else:
            raise ValueError(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        raise e
    #     print("An error occurred:", str(e))

