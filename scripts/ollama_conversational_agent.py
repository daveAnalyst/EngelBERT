from ollama_response import create_response
from IPython.display import HTML, Markdown, display
import os
import warnings
import json
import tempfile
import shutil
warnings.filterwarnings("ignore")

print("All the Libraries are imported")


def creative_stateful(query: str) -> str: 
    """
    Responds to user queries in a creative, imaginative, and expressive manner.

    This agent is activated when the conversation tone is classified as 'creative'.
    It generates responses that are metaphorical, artistic, poetic, or abstract in nature,
    aiming to inspire, provoke thought, or entertain.

    Parameters:
        query (str): The user’s input message.

    Returns:
        str: A creatively inspired response based on the user's message.
    """
    creative_prompt = f"""
            You are a creative assistant who responds with imagination, beauty, and expression.
            
            Your task is to answer the user's message in a way that is:
            - Artistic, poetic, or metaphorical
            - Emotionally evocative or thought-provoking
            - Abstract, whimsical, or story-driven if suitable
            - Original and free-form, like a piece of creative writing
            
            Avoid sounding robotic or overly technical. Feel free to use poetic devices, analogies, or even short stories.
            
        """

    response = create_response(query, system_prompt=creative_prompt)
    result = Markdown(response.message.content)
    #Use display(..) to display it on python
    return result

def science_stateful(query: str) -> str: 
    """
    Responds to user queries in a scientific and analytical manner.

    This agent is activated when the conversation tone is classified as 'scientific'.
    It provides fact-based, logical, and structured responses, often referencing
    scientific concepts, definitions, or explanations.

    Parameters:
        query (str): The user’s input message.

    Returns:
        str: A scientifically reasoned response to the user query.
    """

    science_prompt = f"""
                    You are a scientific assistant. 

                    Your goal is to explain scientific questions in a way that is:
                    - Analytical and based on facts
                    - Logically reasoned
                    - Easy to understand, even for someone with a high school science background
                    - Structured and clear, using bullet points or paragraphs if appropriate

                    Avoid overly complex jargon unless it's essential, and define technical terms when used.
    
                     """
    response = create_response(query, system_prompt=science_prompt)
    result = Markdown(response.message.content)
    return result


class conversational_agent: 
    def __init__(self, username, conv_memory, science_agent, creative_agent): 
        self.creative_agent = creative_stateful
        self.science_agent = science_stateful
        self.username = username
        self.conv_memory = conv_memory
        if os.path.exists(conv_memory): 
            print("ja")
            self.users_conversation = self.load_conversation()
        else: 
            self.users_conversation = {} #{ username: [ {query, response, ...}, ... ] }
        
    def run(self, query, vibe): 
    
        if vibe == "scientific": 
            response = self.science_agent(query)            

        elif vibe == "creative": 
            response = self.creative_agent(query)

        entry = {
            "query": query, 
            "response": response
        }

        #Check if the user is already inside the database
        if self.username not in self.users_conversation: 
            self.users_conversation[self.username] = []

        #Updating conversation query
        self.users_conversation[self.username].append(entry)

        #Updating the json file
        self.save_conversation()
        
        return display(response)

    def save_conversation(self): 
        try:
            with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tf:
                json.dump(self.users_conversation, tf, ensure_ascii=False, indent=3)
                temp_name = tf.name
            shutil.move(temp_name, self.conv_memory)
        except Exception as e:
            print(f"Fehler beim Speichern der Konversation: {e}")

    def load_conversation(self):
        try:
            with open(self.conv_memory, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"No existing conversation file found at {filename}") 

if __name__ == "__main__": 
    agent = conversational_agent("Max", "conversation.json", science_stateful, creative_stateful)
    agent.run("How strong is LLM?", "scientific")

