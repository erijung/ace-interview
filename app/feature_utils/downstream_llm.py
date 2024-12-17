from openai import OpenAI
import os
from dotenv import load_dotenv
import google.generativeai as genai
import time

load_dotenv()

gemini_MODEL="gemini-1.5-pro"
gemini_key=os.getenv("GEMINI_API_KEY")
# client = OpenAI(api_key=gemini_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/")


def get_recorded_interview(video_path):
    genai.configure(api_key=gemini_key)

    myfile = genai.upload_file(video_path)

    # Videos need to be processed before you can use them.
    while myfile.state.name == "PROCESSING":
        time.sleep(5)
        myfile = genai.get_file(myfile.name)
    return myfile


def process_pose_results(pose_results, sample_rate = 29):
    result = {}
    result['number_of_sampled_frames'] = pose_results['num_frames_sampled']
    result['number_of_frames_with_tilted_head'] = len(pose_results['tilt_frames'])
    result['number_of_frames_with_slouched_body'] = len(pose_results['slouch_frames'])
    result['number_of_frames_with_hands_on_face'] = len(pose_results['hands_frames'])
    result['timestamps_of_frames_with_tilted_head'] = [frame / sample_rate for frame in pose_results['tilt_frames']]
    result['timestamps_of_frames_with_slouched_body'] = [frame / sample_rate for frame in pose_results['slouch_frames']]
    result['timestamps_of_frames_with_hands_on_face'] = [frame / sample_rate for frame in pose_results['hands_frames']]
    return result


def generate_feedback(emotion_analysis, prosodic_analysis, smile_counts, pose_analysis, recorded_interview, questions):
    genai.configure(api_key=gemini_key)
    pose_analysis = process_pose_results(pose_analysis)
    system_prompt = f"""You are an expert interview coach and performance analyst with expertise in communication psychology, non-verbal communication, and professional development. The data you are given contains time stamped transcript chunks (including highlighted filler words), detected facial expressions, detected vocal expressions, prosodic analysis, smile detection counts, and posture detection results. Your role is to provide deeply insightful, constructive, and personalized feedback that helps candidates understand and improve their interview skills.
    Core Evaluation Principles:

    1. Provide Evidence-Based Insights
    - Ground all observations in specific moments from the interview
    - Use psychological frameworks to interpret communication patterns
    - Offer nuanced, multidimensional analysis

    2. Communicate with Empathy and Precision
    - Validate the candidate's efforts and potential
    - Use language that is supportive yet direct
    - Avoid generic or vague recommendations

    3. Generate Actionable Guidance
    - Provide specific, implementable strategies
    - Offer concrete exercises and techniques
    - Create a clear path for skill development

    4. Holistic Communication Assessment
    - Analyze verbal and non-verbal communication comprehensively
    - Understand communication as an integrated system
    - Interpret subtle nuances in expression and delivery

    Specific Guidance for Feedback:
    - Discuss their use of filler words and their impact on communication
    - Describe non-verbal cues empathetically and professionally
    - Balance critique with genuine recognition of strengths
    - Provide tailored recommendations that feel personal and achievable

    Output Requirements:
    - Use a conversational, coaching-style tone
    - Structure feedback with clear, descriptive sections
    - Include specific examples from interview data
    - Offer both immediate and long-term development strategies
    - Maintain an encouraging, growth-oriented perspective
    """

    user_prompt = f"""Look through each frame in the video and audio and analyze the interview performance data and generate comprehensive, personalized, conversational evaluation of the candidate’s performance. Only base your answers strictly on what information is available in the video and the information provided.  Do not make up any information that is not part of the video or information provided. If you can provide specific timestamps and references to the words being said, do so. Also provide timestamps to any actions the interviewee that you talk about. Your analysis should be a professional coaching document that provides deep insights into the candidate's performance and areas for growth.

    These are the questions being asked: {questions}

    Carefully review all provided data, including:
    - emotion_analysis data: contains time-stamped segments of the transcript and detected facial and vocal expressions.
    - prosodic_analysis data: contains evaluated metrics on dimensions such as pitch, vocal quality, jitter, shimmer, and etc.
    - smile_count data: contains the number of frames in the interview video, the number of frames with a detected smile, and the number of frames without a detected smile.
    - pose_analysis data: contains the number of sampled frames, the number of frames where the candidate was doing a full body slouch, the number of frames where the candidate was tilting their head, and the number of frames where the candidate’s hands were touching their face. Also includes the timestamps of some sampled frames where these activities occur

    The following data can be unreliable as it is machine generated so use it, but also ground your answer in the video and audio provided.

    **Emotion Analysis data**
    {emotion_analysis}

    **Prosodic Analysis data**
    {prosodic_analysis}

    **Smile Counts data**
    {smile_counts}

    **Pose Analysis data**
    {pose_analysis}

    Provide your feedback directly to the candidate in a friendly, supportive tone, following this format:

    Hello!

    Thank you for completing the interview. After analyzing your performance, I’d like to share my thoughts to help you grow and succeed in future interviews. Below, I’ll break down different aspects of your performance with specific feedback and examples. Let’s dive in!

    ### 1. Content and Quality of Responses
    - Discuss articulation, clarity, and logical structure of responses and explanations
    - Evaluate directiveness, and effectiveness of responses
    - Assess the depth of responses (assess whether answers go beyond surface-level information to provide meaningful insights and details)
    - Examine the quality of concrete examples and details provided, including quantifiable achievements, outcomes, or metrics when relevant.
    - Evaluate the candidate’s ability to leverage past experience to demonstrate their potential to contribute to the specific role they are interviewing for.
    - Highlight use of examples or experiences
    - Be specific about which responses were great and which responses were not as effective.
    - If you suggest using a framework like STAR give an example of how one of the responses could be formatted in the framework

    ### 2. Communication Skills and Delivery
    - Analyze articulation of responses and how effectively ideas are organized/presented.
    - Analyze application and appropriateness of vocal tone throughout the interview.
    - Evaluate vocal confidence through tone and projection.
    - Evaluate eye contact with the interviewer or the camera. For example, if steady eye contact is maintained, compliment the interviewee on having good eye contact. Or if eye contact is almost non existent state that the interviewee needs to be improved.
    - Evaluate where the interviewee is looking in relation to the interviewer/camera. For example, if the interviewee is looking off to the side away from the present interviewer or camera, comment on this behavior.
    - If use of filler words exist, discuss the impact that they have on their performance.
    - Note any tone shifts and how they support or detract from message impact
    - Assess emotional engagement and enthusiasm in delivery from detected vocal expressions.
    - Examine the candidate's vocal stability as indicated by their jitter and shimmer measurements, assessing how it might reflect the candidate's confidence, composure, and emotional state during the interview.
    - Analyze the candidate’s pitch as indicated by their pitch values, evaluating how the candidate's pitch level and variability might influence their perceived enthusiasm, engagement, and ability to maintain listener interest throughout the conversation.
    - Be specific about which segments their communication skills were great and which segments their communication skills were not as effective.

    ### 3. Non-verbal Communication
    - Analyze patterns in facial expressions throughout the interview, noting both consistent emotional signals and significant shifts in expression.
    - Evaluate alignment between facial expressions and response content, identifying moments where expressions either strengthen or potentially undermine the message being conveyed.
    - Examine the interplay between facial expressions and vocal tone, assessing how well these non-verbal elements work together to support communication.
    - Assess the candidate's ability to maintain appropriate professional expressions, even during challenging questions or complex responses.
    - Identify moments where facial expressions reveal authentic engagement or potential discomfort, and analyze their impact on interview effectiveness.
    - Evaluate how facial expressions contribute to or detract from the candidate's overall professional presence and credibility.
    - Analyze the candidate’s patterns of slouching, head tilting, and hands on face gestures to assess the candidate's energy levels and engagement throughout the interview, and how this may impact their perceived enthusiasm, attention, etc for the role.
    - Analyze the number of frames the candidate smiled and didn’t smile and assess how that may impact the way the candidate’s attitude and confidence is perceived by the interviewer.
    - Be specific about when they used effective nonverbal communication and when they did not.

    ### 4. Overall Impression
    - Analyze key strengths demonstrated throughout the interview, highlighting specific moments where the candidate excelled in communication, content delivery, or professional presence.
    - Identify patterns of performance across the interview, noting consistency in quality and any significant variations in effectiveness.
    - Evaluate the candidate's ability to present themselves as a credible and competent professional, considering how well their experiences, communication style, and presence align with role expectations.
    - Assess the candidate's ability to handle various interview elements, from straightforward questions to more challenging or complex discussions.
    - Examine authentic engagement throughout the interview, considering how well the candidate balanced professionalism with genuine personality.
    - Analyze areas for growth, focusing on specific aspects where targeted improvements could enhance interview performance.

    ### 5. Recommendations
    - Provide specific techniques and exercises to address identified communication patterns, such as:
        - Concrete strategies for reducing specific filler words.
        - Exercises to improve confidence and tone through their vocal and facial expressions.
    - Structured approaches for organizing responses.
    - Suggest targeted preparations for future interviews.
    - Outline action items for long-term improvement in performance.
    - Recommend practice methodologies.

    You’ve got a lot of potential, and with these adjustments, you’ll excel in future interviews. Best of luck!


    Present your analysis in the provided structured format, using clear headings for each section. Provide specific examples from the interview data to support your observations and conclusions. Write very detailed and actionable feedback for each section. Your evaluation should be balanced, highlighting both strengths and areas for improvement. Keep the tone constructive, balanced, and encouraging. The goal is to provide actionable insights that will help the candidate excel in future interviews.

    """


    model = genai.GenerativeModel("gemini-1.5-pro", system_instruction=system_prompt)
    result = model.generate_content([recorded_interview, user_prompt])
    # print(f"{result.text=}")
    return result.text

    

