import parselmouth
from parselmouth.praat import call
import statistics
import moviepy.editor as mov
import tempfile

def measurePitch(video_path):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        wav_path = tmp_wav.name
    clip = mov.VideoFileClip(video_path)
    clip.audio.write_audiofile(wav_path)
    f0min = 75
    f0max = 300
    unit = "Hertz"
    sound = parselmouth.Sound(wav_path) # read the sound
    duration = call(sound, "Get total duration") # duration
    pitch = call(sound, "To Pitch", 0.0, f0min, f0max) #create a praat pitch object
    meanF0 = call(pitch, "Get mean", 0, 0, unit) # get mean pitch
    stdevF0 = call(pitch, "Get standard deviation", 0 ,0, unit) # get standard deviation
    harmonicity = call(sound, "To Harmonicity (cc)", 0.01, f0min, 0.1, 1.0)
    hnr = call(harmonicity, "Get mean", 0, 0)
    pointProcess = call(sound, "To PointProcess (periodic, cc)", f0min, f0max)
    localJitter = call(pointProcess, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
    localabsoluteJitter = call(pointProcess, "Get jitter (local, absolute)", 0, 0, 0.0001, 0.02, 1.3)
    rapJitter = call(pointProcess, "Get jitter (rap)", 0, 0, 0.0001, 0.02, 1.3)
    ppq5Jitter = call(pointProcess, "Get jitter (ppq5)", 0, 0, 0.0001, 0.02, 1.3)
    ddpJitter = call(pointProcess, "Get jitter (ddp)", 0, 0, 0.0001, 0.02, 1.3)
    localShimmer =  call([sound, pointProcess], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    localdbShimmer = call([sound, pointProcess], "Get shimmer (local_dB)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    apq3Shimmer = call([sound, pointProcess], "Get shimmer (apq3)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    aqpq5Shimmer = call([sound, pointProcess], "Get shimmer (apq5)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    apq11Shimmer =  call([sound, pointProcess], "Get shimmer (apq11)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    ddaShimmer = call([sound, pointProcess], "Get shimmer (dda)", 0, 0, 0.0001, 0.02, 1.3, 1.6)

    data = {
      "user_wav": {
          "duration": duration,
          "meanF0": meanF0,
          "stdevF0": stdevF0,
          "hnr": hnr,
          "localJitter": localJitter,
          "localabsoluteJitter": localabsoluteJitter,
          "rapJitter": rapJitter,
          "ppq5Jitter": ppq5Jitter,
          "ddpJitter": ddpJitter,
          "localShimmer": localShimmer,
          "localdbShimmer": localdbShimmer,
          "apq3Shimmer": apq3Shimmer,
          "aqpq5Shimmer": aqpq5Shimmer,
          "apq11Shimmer": apq11Shimmer,
          "ddaShimmer": ddaShimmer
      }}

    return data
