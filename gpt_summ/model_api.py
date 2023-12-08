"""
Source to chunk a big corpus of text, summarize the chunks, merge the summaries, and repeat until the document is an acceptable length.

API wrapper taken from archived code from daveshap's project at https://github.com/daveshap/RecursiveSummarizer. 
"""


import openai
import os
from time import time,sleep
import textwrap
import re
import tiktoken as ttk


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

openai.api_key = os.getenv('OPENAI_API_KEY')

def save_file(content, filepath):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def gpt3_completion(prompt, engine='text-davinci-003', temp=0.5, top_p=1.0, tokens=2000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 5
    retry = 0
    while True:
        try:
            response = openai.Completion.create(
                engine=engine,
                prompt=prompt,
                temperature=temp,
                max_tokens=tokens,
                top_p=top_p,
                frequency_penalty=freq_pen,
                presence_penalty=pres_pen,
                stop=stop)
            text = response['choices'][0]['text'].strip()
            text = re.sub('\s+', ' ', text)
            filename = '%s_gpt3.txt' % time()
            with open('gpt3_logs/%s' % filename, 'w+') as outfile:
                outfile.write('PROMPT:\n\n' + prompt + '\n\n==========\n\nRESPONSE:\n\n' + text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


def gpt3_embedding(prompt, engine="text-embedding-ada-002"):
    max_retry = 5
    retry = 0
    while True:
        try:
            response = openai.Embedding.create(
                model=engine,
                input=[prompt])
            embedding = response['data'][0]['embedding']
            return embedding
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)


def chat_completion(prompt,model='gpt-3.5-turbo-16k', temp=0.5, top_p=1.0, tokens=4000, freq_pen=0.25, pres_pen=0.0, stop=['<<END>>']):
    max_retry = 5
    retry = 0
    while True:
        try:
            response = openai.ChatCompletion.create(
                    model = model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temp,
                    max_tokens=tokens,
                    frequency_penalty = freq_pen,
                    presence_penalty = pres_pen,
                    )
            text = response.choices[0].message.content
            text = re.sub('\s+', ' ', text)
            return text
        except Exception as oops:
            retry += 1
            if retry >= max_retry:
                return "GPT3.5 error: %s" % oops
            print('Error communicating with OpenAI:', oops)
            sleep(1)

def token_length_for_model(query: str, model_name: str = 'gpt-3.5-turbo'):
    enc = ttk.encoding_for_model(model_name)
    return len(enc.encode(query))
