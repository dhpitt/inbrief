"""
Source to chunk a big corpus of text, summarize the chunks, merge the summaries, and repeat until the document is an acceptable length.

API wrapper taken from archived code from daveshap's project at https://github.com/daveshap/RecursiveSummarizer. 
"""


import openai
import os
from time import time,sleep
import textwrap
import re


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

# openai.api_key = open_file('openaiapikey.txt')
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

def recursively_summarize(filename: str, prompt_filename:str) -> str:
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
            result = list()
            count = 0
            for chunk in chunks:
                count = count + 1
                prompt = open_file(prompt_filename).replace('<<SUMMARY>>', chunk)
                prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
                summary = gpt3_completion(prompt)
                print('\n\n\n', count, 'of', len(chunks), ' - ', summary)
                result.append(summary)

            save_file('\n\n'.join(result), 'temp.txt')

        else:
            # save_file('\n\n'.join(result), 'output_%s.txt' % time())
            save_file('\n\n'.join(result), 'summary.txt')
            break
    return "\n\n".join(result)

if __name__ == '__main__':
    input_temp = open_file('test.txt')
    save_file(input_temp, 'temp.txt')

    # Continually split, summarize, merge while the length of the final document 
    # is less than 600 words. 

    while True:
        alltext = open_file('temp.txt')
        if len(alltext.split(' ')) > 800: 

            # max davinci text context = 4097 tokens, ~4000 characters
            chunks = textwrap.wrap(alltext, 4000)
            result = list()
            count = 0
            for chunk in chunks:
                count = count + 1
                prompt = open_file('prompt.txt').replace('<<SUMMARY>>', chunk)
                prompt = prompt.encode(encoding='ASCII',errors='ignore').decode()
                summary = gpt3_completion(prompt)
                print('\n\n\n', count, 'of', len(chunks), ' - ', summary)
                result.append(summary)

            save_file('\n\n'.join(result), 'temp.txt')

        else:
            #save_file('\n\n'.join(result), 'output_%s.txt' % time())
            save_file('\n\n'.join(result), 'dsa_summary.txt')


            break
    print("Summary complete.")

