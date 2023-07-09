"""
Celery task messenger. Connects to localhost RabbitMQ broker.
"""
from celery import Celery

from recurse import gpt3_completion

prompt_template = "Write a concise, 50-word summary of the following text with a focus on overarching plot elements:\n\n<<SUMMARY>>\nCONCISE SUMMARY:"

app = Celery('summ_sender', backend='rpc://', broker='pyamqp://')

@app.task
def summarize(chunk: str, idx: int = 0):
    # One worker node: Send a chunk of text to OpenAI.
    prompt = prompt_template.replace("<<SUMMARY>>", chunk)
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
    print("prompt generated.")
    summary = gpt3_completion(prompt)
    print("retrieved summary.")
    return summary, idx



