"""
Source to chunk, send summary tasks to the queue for async processing,
then stitch together the final list of results.
"""

import os

import openai
import textwrap
import numpy as np

from celery_api import embed_one_chunk, embed_one_chunk_with_query, summarize_one_chunk

from gpt_summ.model_api import chat_completion, gpt3_embedding, token_length_for_model
from util import split_str_into_chunks

def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

openai.api_key = os.getenv('OPENAI_API_KEY')

def save_file(content, filepath):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)

def embed_async(in_txt: str, chunk_len: int=3900):
    # exact same logic as brief module's embed, except uses Celery worker queue

    chunks = textwrap.wrap(in_txt, chunk_len) 
    result = []
    async_results = [] 
    for i, chunk in enumerate(chunks):
        # push each chunk summary task onto the queue, keep track of AsyncResult obj
        async_results.append(embed_one_chunk.delay(chunk=chunk,idx=i))

    # sort results by their index, passed in at instantiation for each task
    result = sorted([x.get() for x in async_results], key=lambda x: x[-1])
    return result

def select_informative_pages(query, pages: list, n_best:int=10):
    # get query embedding
    query_embed = np.array(gpt3_embedding(query))
    data = np.stack([p[0] for p in pages]) # one matrix of n rows, 1536 col
    inner_prods = query_embed @ data.T  
    if n_best > len(pages):
        n_best = len(pages)

    inds = sorted(list(inner_prods.argsort()[::-1][:n_best]))
    best_chunks = [pages[i][1] for i in inds]
    return best_chunks

def select_best_chunks(query:str , in_txt: str, chunk_len:int = 3900, n_best:int=10):
    query_embed = gpt3_embedding(query)
    chunks = textwrap.wrap(in_txt, chunk_len) 
    async_results = [] 
    for i, chunk in enumerate(chunks):
        # push each chunk summary task onto the queue, keep track of AsyncResult obj
        async_results.append(embed_one_chunk_with_query.delay(chunk=chunk,
                                                              idx=i, 
                                                              query_embed=query_embed))

    # grab n_best most similar pages
    best_pgs = sorted([x.get() for x in async_results], key=lambda x: x[0],reverse=True)[:n_best]
    
    # return pages in order they're passed in
    sorted_best_pgs = sorted(best_pgs, key=lambda x: x[-1])

    return [x[1] for x in sorted_best_pgs]


def embed_and_polish(in_fname: str, query: str, n_best: int):


    polish_prompt = f"Below are selected pages of an environmental impact statement. \
    Write a concise, informative 800-word summary with an eye towards clarity, focusing on {query}.\
    Ensure that the summary contains an introduction and conclusion.\
            \n<<INPUT>>"

    in_txt = open_file(in_fname)
    #embeddings = embed_async(in_txt)
    #informative_pages = select_informative_pages(query, embeddings, n_best) 

    informative_pages = select_best_chunks(query=query, in_txt=in_txt, n_best=n_best)

    merged_pages = ' '.join(informative_pages)

    token_len = token_length_for_model(merged_pages)
    if token_len < 12000: # if possible, summarize in one pass
        print(f"skipping recursive summary, just returning chat completion")
        result = chat_completion(polish_prompt.replace("<<INPUT>>",merged_pages),
                                 #model='gpt-3.5-turbo-1106',
                                 model='gpt-4-1106-preview',
                                 tokens=4000)
    else: 
        result = recursively_summarize_str_async(merged_pages, query)
    save_file(result, "summary.txt")
    return result

def recursively_summarize_str_async(in_text: str, query: str, summ_length: int = 1000) -> str:
    # uses recursion summ strategy to summarize a string using
    # the async celery worker queue

    # prompt to feed into model
    numwords = str(summ_length)
    polish_prompt = f"Below are selected pages of an environmental impact statement. \
    Summarize them in {numwords} words with an eye towards clarity \
        and informativeness, focusing on {query}:\
            \n<<INPUT>>"
    
    result = []
    while True:
        token_len = token_length_for_model(in_text)
        if token_len < summ_length * 3: # if possible, and text is short enough, summarize in one pass
            in_text = chat_completion(polish_prompt.replace("<<INPUT>>", in_text),model='gpt-3.5-turbo-1106',tokens=summ_length)
            break
        else:
            num_chunks = token_len // 9000 + 1
            chunks = split_str_into_chunks(in_text, num_chunks)
            print(chunks)
            async_results = [] 
            for i, chunk in enumerate(chunks):
            # push each chunk summary task onto the queue, keep track of AsyncResult obj
                async_results.append(summarize_one_chunk.delay(chunk=chunk,
                                                               idx=i, 
                                                               prompt_template = polish_prompt,
                                                               engine='gpt-3.5-turbo-1106',
                                                               tokens=summ_length))
            
                # sort results by their index, passed in at instantiation for each task
            get_results = sorted([x.get() for x in async_results], key=lambda x: x[1])
            print(get_results)
            result = [x[0] for x in get_results]
            in_text = ' '.join(result)
    # in_text is now a summarized string

    return in_text


