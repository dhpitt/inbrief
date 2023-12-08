"""
Celery task messenger. Connects to localhost RabbitMQ broker.
"""
from celery import Celery
import numpy as np

from gpt_summ.model_api import chat_completion, gpt3_embedding

#prompt_template = "Write a concise, 50-word summary of the following text with a focus on overarching plot elements:\n\n<<SUMMARY>>\nCONCISE SUMMARY:"
orig_template = "You are summarizing a small chunk of a much larger document. Write a concise  summary of the following text with a focus on overarching plot elements and an eye toward the final summary:\n\n<<SUMMARY>>\nCONCISE SUMMARY:"

app = Celery('celery_api', backend='rpc://', broker='pyamqp://')

@app.task
def summarize_one_chunk(chunk: str, idx: int = 0, 
                        prompt_template = None,
                        engine: str = 'text-davinci-003',
                        tokens=800):
    # One worker node: Send a chunk of text to OpenAI.
    if prompt_template is not None:
        prompt = prompt_template.replace('<<INPUT>>', chunk)
    else:
        prompt = chunk
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
    print("prompt generated.")
    summary = chat_completion(prompt, model=engine, tokens=tokens)
    print("retrieved summary.")
    return summary, idx


@app.task
def embed_one_chunk(chunk: str, idx: int = 0):
    # One worker node: send a chunk of text and receive an embedding in return
    
    prompt = chunk.encode(encoding='ASCII',errors='ignore').decode()
    print("prompt generated.")
    vec = gpt3_embedding(prompt)
    print("retrieved embedding.")
    return vec, chunk, idx

@app.task
def embed_one_chunk_with_query(chunk: str, idx: int, query_embed: list):
    # One worker node: send a chunk of text and receive an embedding in return
    
    prompt = chunk.encode(encoding='ASCII',errors='ignore').decode()
    print("prompt generated.")
    vec = gpt3_embedding(prompt)
    similarity = np.array(query_embed) @ np.array(vec)
    print("retrieved similarity.")
    return similarity, chunk, idx

