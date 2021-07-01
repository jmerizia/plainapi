import os
from typing import Literal, Any, cast
from uuid import uuid4
import openai  # type: ignore


CACHE_DIR = 'gpt_cache'


def cached_complete(prompt: str, stop: str = '\n', engine: Literal['davinci', 'curie'] = 'davinci', use_cache: bool = True) -> str:
    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    separator = '\n===========\n'
    if use_cache:
        # Check the cache
        cache_files = [os.path.join(CACHE_DIR, p) for p in os.listdir(CACHE_DIR)]
        for fn in cache_files:
            with open(fn, 'r') as f:
                query, result = f.read().split(separator)
            if query == prompt:
                return result

    response = cast(Any, openai.Completion.create(
        engine=engine,
        prompt=prompt,
        max_tokens=64,
        temperature=0,
        stop=stop,
    ))
    result = response['choices'][0]['text']

    # Add to the cache
    cache_file = os.path.join(CACHE_DIR, str(uuid4()))
    with open(cache_file, 'w') as f:
        f.write(prompt + separator + result)

    return result
