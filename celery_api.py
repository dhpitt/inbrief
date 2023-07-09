"""
Celery task messenger. Connects to localhost RabbitMQ broker.
"""
from celery import Celery

from gpt_summ.recurse import gpt3_completion

#prompt_template = "Write a concise, 50-word summary of the following text with a focus on overarching plot elements:\n\n<<SUMMARY>>\nCONCISE SUMMARY:"
prompt_template = "You are summarizing a small chunk of a much larger document. Write a concise, 50-word summary of the following text with a focus on overarching plot elements and an eye toward the final summary:\n\n<<SUMMARY>>\nCONCISE SUMMARY:"

app = Celery('celery_api', backend='rpc://', broker='pyamqp://')

@app.task
def summarize_one_chunk(chunk: str, idx: int = 0):
    # One worker node: Send a chunk of text to OpenAI.
    prompt = prompt_template.replace("<<SUMMARY>>", chunk)
    prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
    print("prompt generated.")
    summary = gpt3_completion(prompt)
    print("retrieved summary.")
    return summary, idx


