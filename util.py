# utility functions with no ML
from math import ceil

def split_str_into_chunks(in_str: str, num_chunks: int):
    
    doc_len = len(in_str)
    chunk_len = ceil(doc_len / num_chunks)
    splits = list(range(0, doc_len, chunk_len))
    if splits[-1] < doc_len:
        splits.append(doc_len)
    print(splits)
    chunks = [in_str[splits[i]:splits[i+1]] for i in range(len(splits[:-1]))]
    return chunks


   
   
