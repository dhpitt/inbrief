"""
Source to chunk, send summary tasks to the queue for async processing,
then stitch together the final list of results.
"""

import celery
import openai
import os
from time import time,sleep
import textwrap
import re

from celery_api import summarize_one_chunk


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

# openai.api_key = open_file('openaiapikey.txt')
openai.api_key = os.getenv('OPENAI_API_KEY')

def save_file(content, filepath):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

def recursively_summarize_async(filename: str) -> str:
    # exact same logic as brief module's summarize, except uses Celery worker queue
    input_temp = open_file(filename)
    save_file(input_temp, 'temp.txt')

    # Continually split, summarize, merge while the length of the final document
    # is less than 600 words.
    result = []
    while True:
        alltext = open_file('temp.txt')
        if len(alltext.split(' ')) > 1000: 
            # max davinci text context = 4097 tokens, ~4000 characters
            chunks = textwrap.wrap(alltext, 4000)
            result = []
            async_results = [] 
            for i, chunk in enumerate(chunks):
                # push each chunk summary task onto the queue, keep track of AsyncResult obj
                async_results.append(summarize_one_chunk.delay(chunk=chunk,idx=i))
            
            # sort results by their index, passed in at instantiation for each task
            get_results = sorted([x.get() for x in async_results], key=lambda x: x[1])
            result = [x[0] for x in get_results]
            save_file('\n\n'.join(result), 'temp.txt')

        else:
            # save_file('\n\n'.join(result), 'output_%s.txt' % time())
            save_file('\n\n'.join(result), 'summary.txt')
            #save_file('\n\n'.join(result), 'summary.txt')
            break
    return "\n\n".join(result)
