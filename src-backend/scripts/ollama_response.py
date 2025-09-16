#!/usr/bin/env python
# coding: utf-8

# In[15]:


from ollama import chat
from ollama import ChatResponse
from ollama import AsyncClient
import ollama
import io
import base64
from transformers import pipeline
from markdown import markdown
from PIL import Image


# In[20]:


def create_response(prompt: str, system_prompt: str, image_path=None, model='gemma3'): 
    
    #Check if model is available
    try: 
        ollama.chat(model) 
    except ollama.ResponseError as e: 
        print('Error: ', e.error)
        if e.status_code==404: 
            #To download the model, if it isnt locally available. 
            ollama.pull(model) 

    messages = []

    if system_prompt: 
        messages.append({'role': "system", "content": system_prompt})
    
    if image_path:
        try: 
            #Read Image and convert to base64, so that olama can read it. 
            with Image.open(image_path) as img: 
                buffered = io.BytesIO() 
                img.save(buffered, format="JPEG")
                img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

            messages.append(
                {
                    'role': 'user', 
                    'content': prompt,
                    'images' : [img_str]
                }
            )

        except FileNotFoundError: 
            return f"Error: Image file not found at {image_path}"
        except Exception as e: 
            return f"Error processing image: {e}"
    else: 
            messages.append(
                {
                    'role': 'user', 
                    'content': prompt
                }
            )

    response = chat(model=model, messages = messages)
    return response


# In[ ]:




