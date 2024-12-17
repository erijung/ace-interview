from hume import AsyncHumeClient
from hume.expression_measurement.batch import Face, Prosody, Models
from hume.expression_measurement.batch.types import InferenceBaseRequest
import asyncio
import os
from dotenv import load_dotenv
import json
import heapq


load_dotenv()

client = AsyncHumeClient(api_key=os.getenv("HUME_API_KEY"))

async def upload_to_hume(video_path):

    local_filepaths = [open(video_path, mode="rb"), ]
    
    # Create configurations for each model you would like to use (blank = default)
    face_config = Face()
    prosody_config = Prosody()

    # Create a Models object
    models_chosen = Models(face=face_config, prosody=prosody_config)
    
    # Create a stringified object containing the configuration
    stringified_configs = InferenceBaseRequest(models=models_chosen)
    # Start an inference job and print the job_id
    job_id = await client.expression_measurement.batch.start_inference_job_from_local_file(
        json=stringified_configs, file=local_filepaths
    )
    return job_id

async def get_predictions(job_id):
    """Retrieves predictions for a given job ID.
    Includes a loop to check job status and waits for completion.
    """
    import asyncio
    while True:  
        try:
            predictions = await client.expression_measurement.batch.get_job_predictions(job_id)
            return json.loads(predictions[0].json())['results'] 
        except Exception as e:
            if e.status_code == 400 and e.body.get("message") == "Job is in progress.":
                await asyncio.sleep(10) 
            else:
                raise e  


def transform_predictions(hume_output, transcript):
  results = []
  prosody_predictions = hume_output['predictions'][0]['models']['prosody']['grouped_predictions'][0]['predictions']
  face_expressions_predictions = hume_output['predictions'][0]['models']['face']['grouped_predictions'][0]['predictions']
  enriched_transcript = transcript['chunks']
  prosody_index = 0
  transcript_index = 0
  face_index = 0
  relevant_emotions = set(['Amusement', 'Anxiety', "Awkwardness", "Boredom",
                         "Calmness", "Concentration", "Confusion",
                         "Contemplation", "Contentment", "Desire",
                         "Determination", "Disappointment", "Distress", "Doubt",
                         "Excitement", "Interest", "Joy", "Pride", "Realization",
                         "Sadness", "Satisfaction", "Shame",
                         "Surprise (negative)","Surprise (positive)" ])
  while prosody_index < len(prosody_predictions):
    record = {}
    record['beginning_timestamp'] = prosody_predictions[prosody_index]['time']['begin']
    record['ending_timestamp'] = prosody_predictions[prosody_index]['time']['end']
    record['transcript_chunk'] = ""
    while transcript_index < len(enriched_transcript) and enriched_transcript[transcript_index]['timestamp'][0] < record['ending_timestamp']:
      record['transcript_chunk'] += enriched_transcript[transcript_index]['text'] + " "
      transcript_index += 1

    vocal_characteristics = []
    vocal_heap = []
    for emotion in prosody_predictions[prosody_index]['emotions']:
      if emotion['name'] in relevant_emotions and emotion['score'] >= 0.15:
        if len(vocal_heap) < 4:
          heapq.heappush(vocal_heap, (emotion['score'] * -1, emotion['name']))
        else:
          heapq.heappushpop(vocal_heap, (emotion['score'] * -1, emotion['name']))
    while vocal_heap:
      vocal_characteristics.append(heapq.heappop(vocal_heap)[1])
    record['top_vocal_characteristics'] = vocal_characteristics

    face_expressions = {}
    face_heap = []
    count = 0
    while face_index < len(face_expressions_predictions):
      if face_expressions_predictions[face_index]['time'] <= record['ending_timestamp']:
        for emotion in face_expressions_predictions[face_index]['emotions']:
          if emotion['name'] in relevant_emotions:
            if emotion['name'] not in face_expressions:
              face_expressions[emotion['name']] = emotion['score']
            else:
              face_expressions[emotion['name']] += emotion['score']
        count += 1
        face_index += 1
      else:
        break
    for emotion in face_expressions:
      averaged_score = face_expressions[emotion] / count
      if averaged_score > 0.22:
        if len(face_heap) < 4:
          heapq.heappush(face_heap, (averaged_score * -1, emotion))
        else:
          heapq.heappushpop(face_heap, (averaged_score * -1, emotion))

    top_face_expressions = []
    while face_heap:
      top_face_expressions.append(heapq.heappop(face_heap)[1])
    record['top_face_expressions'] = top_face_expressions
    results.append(record)
    prosody_index += 1
  return results












