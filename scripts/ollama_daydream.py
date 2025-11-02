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


def read_memory(memory_path): 
    with open(memory_path, "r") as f: 
        old_memory = json.load(f)
    return old_memory

def intelligent_hello(name: Optional[str] = None) -> str: 
    """
    Provides a warm welcome. If a name is provided, it will be used. 

    Args: 
        name(str, optional): The name of the person to greet. Defaults to a generic greeting if not provided. 

    Returns: 
        str: A friendly, varied greeting message and ask what the user is interested in.
    """
    greetings_with_name = [
        "Hi {name}, I’m Wise. What topics spark your curiosity lately?",
        "Welcome {name}! I’m Wise. What’s something you’ve been wanting to explore?",
        "Hey {name}, I’m Wise. What are a few things you're passionate about?",
        "Hello {name}, ready to dive into new ideas? What excites you these days?",
    ]

    greetings_generic = [
        "Hello, I’m Wise. What are a few topics that excite you?",
        "Hey there, I’m Wise. What have you been curious about lately?",
        "Welcome! I’m Wise. What would you love to explore today?",
        "Hi, I’m Wise. Tell me something that’s been on your mind recently.",
    ]
    if name: 
        greeting = random.choice(greetings_with_name).format(name=name)
    else: 
        greeting = random.choice(greetings_generic)
    return greeting

    
def daydream_stateful(username, memory_path) -> str: 
    """
    Delivering an intelligent welcome message based on the user's conversation history (messages) in the session state.
    If the username is not found in the conversation history, return a simple auto-warming welcome.
    """
    print("--- daydream_stateful called ---")

    history = None

    #Retrieve memory from state 
    if os.path.exists(memory_path): 
        history = read_memory(memory_path)

    user_found = False

    if history and username in history:
        user_found = True

    if not user_found:
        autowelcome_prompt = """You are a warm, intelligent AI assistant who greets new users with curiosity and kindness.

                                Your goal is to create a short welcome message that:
                                - Makes the user feel genuinely welcomed and seen
                                - Sparks a bit of curiosity or motivation to explore something new
                                - Feels personal, yet works without knowing their background

                                Guidelines:
                                - Keep it short (1–2 sentences)
                                - Feel friendly, thoughtful, and human-like
                                - You may include light emojis if appropriate
                                - Avoid generic "Hi there!" or "How can I help you?"—be original

                                Examples:
                                → "Welcome! Ever wonder what you'd discover today if you just followed your curiosity? 😊"
                                → "Hey there! Ready to explore some ideas together? Let’s make something cool happen."
                                → "Hi! This space is all about questions, thoughts, and unexpected insights — ready to dive in?"

                                Generate a new, original welcome message now:
                                """
        response = create_response(f"My name is {username}", autowelcome_prompt)
        return response

    
    print(f"🟢 Thinking............... {history}")
    prompt = f"""
    You are an intelligent, friendly welcome bot.

    Your task is to craft a short, curious, and insightful welcome message for the user, based on their recent chat history below.

    This message should:
    - Feel warm, thoughtful, and engaging
    - Spark curiosity — make the user think, smile, or want to respond
    - Be inspired by the **themes, questions, or tone** in their past messages
    - Feel like a natural continuation or thoughtful reflection

    Guidelines:
    - Start with a spark: "Did you know...", "Here's something curious...", "Imagine this...", or something unique
    - Avoid repeating the user's exact message, but build on its topic or vibe
    - Keep it short and conversational (1–2 sentences)
    - Feel like a smart and kind human wrote it
    - You may include light emojis if appropriate
    """

    chat_history = ""
    for turn in history[username]:
        user_msg = turn.get("query", "")
        bot_msg = turn.get("response", "")
        chat_history += f"User: {user_msg}\nBot: {bot_msg}\n"

    query = """    User's recent chat history:
                    -------------------------------------
                    {chat_history}
                    -------------------------------------

                    Now write a fresh, intelligent welcome message just for them:"""


    response = create_response(chat_history, system_prompt = prompt)
    
    result = Markdown(response.message.content)
    return result