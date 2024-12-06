import numpy as np
import streamlit as st
import tempfile
from feature_utils.pose_detection import *
from feature_utils.smile import *

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
            with tempfile.NamedTemporaryFile(delete=False, suffix=".avi") as temp_video:
                temp_video.write(video.read())
                temp_video_path = temp_video.name
            pose_results = pose_detection(temp_video_path)
            smile_results = detect_smiles_video(temp_video_path)
            feedback = """
Hello!
Thank you for completing the interview. After analyzing your performance, I’d like to share my thoughts to help you grow and succeed in future interviews. Below, I’ll break down different aspects of your performance with specific feedback and examples. Let’s dive in!

### 1. Content and Quality of Responses

Your responses demonstrated a mix of strengths and areas for improvement. You effectively conveyed your academic background and extracurricular involvements, showcasing your passion for computational biology and commitment to community service.  For instance, your explanation of your Course 6-7 studies at MIT clearly highlighted your interest in the intersection of computer science and biology. Your description of Camp Kesem and Amphibious Achievement illustrated your leadership experience and dedication to helping others.  You successfully quantified your fundraising achievements for Camp Kesem, mentioning the substantial amount of over $50,000 raised.  This added weight to your leadership narrative.
However, your responses to behavioral questions could benefit from greater depth and structure. When asked about a time you demonstrated leadership, your focus on the fundraising auction, while impactful, could be enhanced by detailing specific leadership challenges faced and how you overcame them.  For example, instead of just saying you “organized everyone into committees and groups,” you could describe a specific instance of resolving conflict or motivating team members.
Similarly, when discussing a team challenge, your example lacked specificity.  While you mentioned unequal work distribution, you didn’t clearly outline the problem-solving steps taken.  Instead of simply stating that you “talked and didn’t really get it out,” describe the specific communication strategies employed and the ultimate resolution.  Focus on actionable steps and quantifiable outcomes whenever possible.  Relating your experiences back to the specific job requirements would also strengthen your responses.

### 2. Communication Skills and Delivery

Your vocal tone remained relatively calm and consistent throughout the interview, suggesting composure under pressure. However, your responses were frequently punctuated with filler words like “um,” “uh,” and “so.”  For example, the transcript shows multiple instances of these fillers within short spans of time, like in the segment discussing your academic background: '[UM] so I guess have you looked at my resume or should I? All right. So I guess I’m a course six seven here at MIT [UH]...' These fillers, while natural in conversation, can detract from the clarity and impact of your message in a formal setting like an interview.
Your vocal expression data shows a mix of contemplation, concentration, and calmness, which aligns with the content of your responses.  However, injecting more enthusiasm and energy, particularly when discussing your interests and experiences, could significantly enhance your overall presentation.  The prosodic analysis reveals a relatively consistent pitch and low jitter/shimmer, indicating vocal stability.  However, varying your pitch more dynamically could add expressiveness and help maintain listener engagement.
While you generally maintained a professional tone, there’s room for improvement in projecting more confidence and enthusiasm.  For example, when discussing why you should be hired, your vocal characteristics according to the data show “Calmness, Contemplation, Determination, and Interest.” While these are positive, adding vocal cues of “Enthusiasm” and “Passion” would strengthen your closing statement.

### 3. Non-verbal Communication
Your facial expressions, as captured in the emotion analysis, present a mixed picture. While expressions of interest and calmness are frequently detected, there are also instances of awkwardness, boredom, and disappointment, especially during the initial part of the interview.  This disconnect between your verbal message and facial cues could inadvertently signal a lack of genuine enthusiasm.  For example, while describing your passion for computational biology, your detected facial expressions include “Doubt,” “Boredom,” “Amusement,” and “Awkwardness.” This misalignment can dilute the impact of your message.
The pose analysis reveals a frequent pattern of head tilting, occurring in numerous frames throughout the interview. This, along with the low smile count (only 2 smiles detected in the entire video), could be interpreted as a lack of confidence or engagement. While maintaining professional composure is essential, incorporating more natural smiles and minimizing repetitive head tilts could significantly enhance your overall presence and create a more positive impression.  Avoiding touching your face or slouching, as indicated by the absence of such instances in the pose analysis, is a positive aspect of your non-verbal communication.

### 4. Overall Impression
You demonstrate potential as a candidate with a clear academic focus and relevant extracurricular experiences. Your composure and consistent vocal tone suggest an ability to handle pressure. However, a lack of depth and structure in responses to behavioral questions, coupled with frequent filler words and inconsistent non-verbal cues, slightly diminished the overall impact of your interview performance.

### 5. Recommendations
* **Filler Word Reduction:** Practice the “pause and breathe” technique.  When you feel the urge to use a filler word, consciously pause, take a breath, and then continue your sentence.  Record yourself answering common interview questions and identify your most frequent fillers. Develop replacement phrases or simply embrace silence.
* **Non-verbal Enhancement:** Practice smiling genuinely when discussing topics that excite you.  Review the recording of your interview and note instances of repetitive head tilting.  Consciously minimize these gestures.  Maintain eye contact to project confidence and engagement.
* **Response Structuring:** Utilize the STAR method (Situation, Task, Action, Result) to organize your responses to behavioral questions.  Focus on providing concrete examples with quantifiable achievements and clear problem-solving steps. Connect your experiences back to the specific requirements of the role.  Practice answering common behavioral questions aloud, focusing on clarity, conciseness, and impact.
* **Vocal Delivery:** Practice speaking with varying pitch and intonation to inject more enthusiasm and dynamism into your voice. Record and analyze your practice sessions, paying attention to vocal tone and projection.
You’ve got a lot of potential, and with these adjustments, you’ll excel in future interviews. Best of luck"""

            st.header("Results:")
            st.json(smile_results)
            #st.markdown(feedback)
            st.download_button(label = "Save feedback as .txt",
                       data = str(feedback),
                       file_name = "ace_interview_feedback.txt")

if __name__ == "__main__":
    main()
