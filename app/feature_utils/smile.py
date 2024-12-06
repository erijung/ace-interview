import cv2

# read haar cascade for face detection
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# read haar cascade for smile detection
smile_cascade = cv2.CascadeClassifier('haarcascade_smile.xml')

def detect_smile(img):
  # read input image
  #img = cv2.imread(img)

  # convert the image to grayscale
  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

  # Detects faces in the input image
  faces = face_cascade.detectMultiScale(gray, 1.3, 5)

  # loop over all the faces detected
  for (x,y,w,h) in faces:

    roi_gray = gray[y:y+h, x:x+w]

    # detecting smile within the face roi
    smiles = smile_cascade.detectMultiScale(roi_gray, 1.8, 20)
    if len(smiles) > 0:
        return 1

  return 0

def detect_smiles_video(video_path):
    # Open video file
    cap = cv2.VideoCapture(video_path)

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    smiles = 0
    nonsmiles = 0
    count = 0
    while cap.isOpened():
    #for i in np.arange(1000): #first 1000 frames, use the while loop in the above line for whole video
        ret, frame = cap.read()
        if not ret:
            break  # Exit the loop if there are no more frames

        if detect_smile(frame):
          smiles += 1
        else:
          nonsmiles += 1

        count += 1

#        if count % 500 == 0:
#          print(smiles, nonsmiles, count)


    # Release everything once job is finished
    cap.release()

    data = {
    "user_video": {
        "smiles": smiles,
        "nonsmiles": nonsmiles,
        "frame_count": count
    }}

    return data

"""
# Example usage:
smiles, nonsmiles, count = detect_smiles_video(local_file_path)
print(video + " Final:")
print(smiles, nonsmiles, count)
data = {
    video[7:-4]: {
        "smiles": smiles,
        "nonsmiles": nonsmiles,
        "frame_count": count
    }}
# Write the JSON file
with open(file_name, 'w') as file:
    json.dump(data, file, indent=4)
"""
