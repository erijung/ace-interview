import numpy as np
import streamlit as st
import tempfile
from feature_utils.pose_detection import *
from feature_utils.smile import *
from feature_utils.prosody import *
from feature_utils.emotion_analysis import *
from feature_utils.crisperwhisper import *
from feature_utils.downstream_llm import *

def main():
    st.set_page_config(
    page_title="AceInterview",
    page_icon=":briefcase:",
    layout="centered",
        menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "**UC Berkeley 5th Year MIDS Fall 2024 Capstone Project** by Eric Jung, Sean Wei, Parker Brailow, Naveen Sukumar"
    })

    st.title("Welcome to AceInterview!")

    "AceInterview is an AI practice interview platform that analyzes and \
    provides feedback on user posture, speaking tone, eye contact, and other \
    key interview behaviors."

    "To get started, please select an interview question below:"

    questions = ["",
                 "Please introduce yourself.",
                 "Talk about a time when you demonstrated leadership.",
                 "Describe a time when you were working with a team and faced a challenge. How did you overcome the problem?",
                 "What is one of your weaknesses and how do you plan to overcome it?",
                 "Why do you think you should be hired?",
                 "(Randomly select an interview question)",
                 "(Enter your own custom interview question)"]
    question = st.selectbox("*Select an interview question*", options = questions)


    if question == "":
        "**Please select a question from the above dropdown menu before proceeding.**"
    if question != "":
        if question == questions[-2]:
            question = np.random.choice(questions[1:-2])
        if question == questions[-1]:
            question = st.text_input("*Enter your custom interview question*")
        st.markdown("**Your question:**" + " " + question)


    st.markdown('##')
    "Next, please record a video of yourself responding to the question. \
    Then, upload the video file in the space below and hit the \
    **Generate feedback** button to begin the process."

    video = st.file_uploader("*Upload interview video file*", type=["avi", "mp4"])

    begin = st.button("**Generate feedback**")
    if begin:
        if question == "":
            "**Error:** No question selected. Please select a question from the dropdown menu above."
        elif video is None:
            "**Error:** No video uploaded. Please upload a video file in the space above."
        else:
            st.write("Processing video. This may take a few minutes...")
            # Save the uploaded video file to a temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                temp_video.write(video.read())
                temp_video_path = temp_video.name

            upload_details = get_upload_url("ace-interview")
            upload_url = upload_details["url"]
            transcript_file_name = upload_details["file"]

            upload_video_to_presigned_url(upload_url, temp_video_path)
            hume_job_id =upload_to_hume(temp_video_path)

            pose_results = pose_detection(temp_video_path)
            smile_results = detect_smiles_video(temp_video_path)
            prosody_results = measurePitch(temp_video_path)

            emotion_preds = get_predictions(hume_job_id)
            enriched_transcript = get_transcript(transcript_file_name)
            emotion_results = transform_predictions(emotion_preds, enriched_transcript)

            interview_video = get_recorded_interview(temp_video_path)
            llm_feedback = generate_feedback(emotion_results, prosody_results, smile_results, pose_results, interview_video)


            st.header("Results:")
            st.markdown(llm_feedback)
            st.download_button(label = "Save feedback as .txt",
                       data = str(feedback),
                       file_name = "ace_interview_feedback.txt")

if __name__ == "__main__":
    main()
