import math
import json
import os
import cv2
import mediapipe as mp
import numpy as np
from io import BytesIO
import tempfile

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

def calculate_angle(a, b, c):
    """Calculate the angle between three points (shoulder, neck, hip)."""
    a = np.array(a)  # Shoulder
    b = np.array(b)  # Neck or Spine
    c = np.array(c)  # Hip

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360.0 - angle

    return angle

# Function to calculate Euclidean distance
def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def detect_front_slouching(landmarks):
    """ Detect if someone is slouching forward based on body landmarks. """
    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
    left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
    neck = [(left_shoulder[0] + right_shoulder[0]) / 2, (left_shoulder[1] + right_shoulder[1]) / 2]  # Midpoint of shoulders

    # Calculate midpoint of hips
    hips_mid = [(left_hip[0] + right_hip[0]) / 2, (left_hip[1] + right_hip[1]) / 2]

    # Calculate angle between neck-shoulders and neck-hips
    angle = calculate_angle(left_shoulder, neck, hips_mid)

    if angle < 75:  # Adjust threshold as needed for detecting slouching
        return True, angle
    return False, angle


def detect_side_slouching(landmarks, image, threshold = 10):
    """ Detect if someone is slouching from one side to the other"""
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]

    left_shoulder_x = left_shoulder.x * image.shape[1]
    left_shoulder_y = left_shoulder.y * image.shape[0]
    right_shoulder_x = right_shoulder.x * image.shape[1]
    right_shoulder_y = right_shoulder.y * image.shape[0]

    # Calculate the slope between the two shoulders
    delta_x = right_shoulder_x - left_shoulder_x
    delta_y = right_shoulder_y - left_shoulder_y

    if delta_x != 0:  # Avoid division by zero
        slope = delta_y / delta_x
        # Calculate the angle in degrees
        angle = math.degrees(math.atan(slope))

        # Check if the angle exceeds the threshold
        if abs(angle) > threshold:
            return True, angle
    return False, angle


def detect_head_tilt(landmarks, image, threshold = 5):
    shoulder_left = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
    shoulder_right = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
    nose = landmarks[mp_pose.PoseLandmark.NOSE.value]

    # Convert relative coordinates to absolute pixel values
    left_shoulder_x = shoulder_left.x * image.shape[1]
    left_shoulder_y = shoulder_left.y * image.shape[0]
    right_shoulder_x = shoulder_right.x * image.shape[1]
    right_shoulder_y = shoulder_right.y * image.shape[0]
    nose_x = nose.x * image.shape[1]
    nose_y = nose.y * image.shape[0]

    # Calculate midpoint between shoulders
    shoulder_mid_x = (left_shoulder_x + right_shoulder_x) / 2
    shoulder_mid_y = (left_shoulder_y + right_shoulder_y) / 2

    # Calculate angle between the vertical line (nose) and shoulder line
    delta_x = nose_x - shoulder_mid_x
    delta_y = nose_y - shoulder_mid_y

    angle = math.degrees(math.atan2(delta_y, delta_x)) + 90

    # Detect if the head is tilted beyond the threshold
    if abs(angle) > threshold:
        return True, angle
    else:
        return False, angle


def detect_hands_on_face(pose_results, hands_results, image, threshold = 50):
    if pose_results.pose_landmarks and hands_results.multi_hand_landmarks:
        # Extract face landmarks (nose, mouth, etc.)
        landmarks = pose_results.pose_landmarks.landmark

        coordinates = {}
        coordinates['nose'] = (landmarks[mp_pose.PoseLandmark.NOSE.value].x, landmarks[mp_pose.PoseLandmark.NOSE.value].y)
        coordinates['mouth_left'] = (landmarks[mp_pose.PoseLandmark.MOUTH_LEFT.value].x, landmarks[mp_pose.PoseLandmark.MOUTH_LEFT.value].y)
        coordinates['mouth_right'] = (landmarks[mp_pose.PoseLandmark.MOUTH_RIGHT.value].x, landmarks[mp_pose.PoseLandmark.MOUTH_RIGHT.value].y)
        coordinates['mouth'] = ((coordinates['mouth_left'][0] + coordinates['mouth_right'][0]) / 2, (coordinates['mouth_left'][1] + coordinates['mouth_right'][1]) / 2)
        coordinates['left_eye'] = (landmarks[mp_pose.PoseLandmark.LEFT_EYE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_EYE.value].y)
        coordinates['right_eye'] = (landmarks[mp_pose.PoseLandmark.RIGHT_EYE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_EYE.value].y)

        # Process each detected hand
        for hand_landmarks in hands_results.multi_hand_landmarks:
            index_finger_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image.shape[1]
            index_finger_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image.shape[0]

            for i in coordinates:
                x_px = coordinates[i][0] * image.shape[1]
                y_px = coordinates[i][1] * image.shape[0]
                if calculate_distance(index_finger_x, index_finger_y, coordinates[i][0], coordinates[i][1]) <= threshold:
                    return True
            return False
    return False

def pose_detection(uploaded_file):
    if uploaded_file is None:
        return "No video file uploaded."

    # Save the uploaded video file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".avi") as temp_video:
        temp_video.write(uploaded_file.read())
        temp_video_path = temp_video.name

    cap = cv2.VideoCapture(temp_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)  # Frames per second
    frame_interval = int(fps / 3)   # Process every Nth frame for 3 FPS sampling

    num_frames = 0
    num_frames_sampled = 0

    slouch_frames = []
    hands_frames = []
    tilt_frames = []



    with mp_pose.Pose() as pose, mp_hands.Hands() as hands:
        while cap.isOpened():
            num_frames += 1
            ret, frame = cap.read()
            if not ret:
                break

            # Skip frames to achieve 3 FPS sampling
            if num_frames % frame_interval != 0:
                continue

            num_frames_sampled += 1
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image_rgb)
            hands_results = hands.process(image_rgb)

            if results.pose_landmarks:
                slouching, angle = detect_side_slouching(results.pose_landmarks.landmark, image_rgb, 10)
                if slouching:
                    slouch_frames.append(num_frames)

                hands_on_face = detect_hands_on_face(results, hands_results, image_rgb, threshold=50)
                if hands_on_face:
                    hands_frames.append(num_frames)
                else:
                    head_tilt, angle = detect_head_tilt(results.pose_landmarks.landmark, image_rgb, 20)
                    if head_tilt:
                        tilt_frames.append(num_frames)

    cap.release()

    results = {
        'num_frames_sampled': num_frames_sampled,
        'slouch_frames': slouch_frames,
        'hands_frames': hands_frames,
        'tilt_frames': tilt_frames
    }

    return results
