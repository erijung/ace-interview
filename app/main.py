import numpy as np
import streamlit as st
from feature_utils.pose_detection import *

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

    "AceInterview is an AI practice interview platform which analyzes and \
    provides feedback on user posture, speaking tone, eye contact, and other \
    key interview behaviors."

    "To get started, please select an interview question below:"

    questions = ["",
                 "Describe a time you worked as part of a team.",
                 "Describe your most challenging project.",
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
            pose_results = pose_detection(video)

            feedback = pose_results
            st.header("Results:")
            st.json(feedback)
            st.download_button(label = "Save feedback as .txt",
                       data = str(feedback),
                       file_name = "ace_interview_feedback.txt")

if __name__ == "__main__":
    main()
