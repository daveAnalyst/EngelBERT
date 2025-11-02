#!/usr/bin/env python
# coding: utf-8

# In[2]:

from ollama_response import create_response
from IPython.display import HTML, Markdown, display
import os
import warnings
import json
import tempfile
import shutil
import random
from typing import Optional
warnings.filterwarnings("ignore")

print("All the Libraries are imported")

def vibe_stateful(query) -> str: 
    """Classifying the last_message based on session state as vibe"""

    code_prompt = f"""
    You are a vibe Detector. 
    Given Data(str) below. Classify its tone as either 'scientific' or 'creative'. 
    
    Classification Instruction: 
    ---------------------------------
    You are a vibe-detection agent. Given a user's messages, classify its tone as one of the following:
    1. 'scientific' - The user is analytical, precise, logical or technical. They may ask for explanations, data, or structured reasoning.
    2. 'creative' - The user is imaginative, metaphorical, poetic and artistic. They may be expressing abstract ideas, inventing concepts.
    3. None - IF the user's message is greeting/farewell (example: hi, hallo, hey, bye, see you)
    
    Return ONLY one word: 'scientific' or 'creative'. 
    
    
    Examples:
        - "Can you explain how gradient descent works in machine learning?" → scientific
        - "What if the stars were just neutrons in the brain of the universe?" → creative
        - "How do LLMs store and recall information?" → scientific
        - "Let's invent a theory where gravity is made of music." → creative 
    
    ------------------------------------
    """
    
    response = create_response(query, code_prompt)
    
    result = Markdown(response.message.content)
    return result

