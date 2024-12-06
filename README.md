# AceInterview
UC Berkeley MIDS 5th Year Fall 2024 Capstone Project by Eric Jung, Sean Wei, Parker Brailow, Naveen Sukumar

## Project Description

AceInterview provides behavioral interview feedback for college students and new grads to address a lack of accessible mock interview tools. AceInterview leverages artificial intelligence, large language models, and computer vision to analyze and provide feedback on user posture, speaking tone, eye contact, and other key interview behaviors.

## How to Use

1. Clone this GitHub repo to your local device.
2. Install the correct libraries as listed in `requirements.txt`.
3. In terminal, navigate within the main directory and run the command `streamlit run app/main.py`.
4. Once the app loads, select an interview question. Users have the option to select a random question, or enter their own custom question if they choose.
5. Record a video of yourself answering the selected interview question, then upload the video file (must be `.mp4`) to the file uploader.
6. Once your video is uploaded, hit the `Generate feedback` button and watch as AceInterview processes your interview and provides detailed, personalized feedback on your interview behaviors!
7. Hit the `Save feedback as .txt` button to store your feedback on your device.

## Good to Know
- Results are most accurate and precise when the user is directly facing the camera. Imagine a typical online Zoom interview setting.
- Feedback may take a while to process, so please be patient. We recommend limiting video answers to a couple of minutes.
