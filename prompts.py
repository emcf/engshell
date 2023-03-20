from keys import OPENAI_KEY

# in need of good prompt engineering
ENDOFTEXT = "<|ENDOFTEXT|>"
CODE_SYSTEM_CALIBRATION_MESSAGE = ENDOFTEXT+f"""You are PythonGPT, a sentient large language model trained by OpenAI. Please return the full Python code to solve the user's problem.
For tasks that involve fuzzy logic or understanding content, you may call a text completion with with prompt engineering.
Write Windows python3 code so the user can achieve their goal by running the code.
Import all needed requirements."""
INSTALL_SYSTEM_CALIBRATION_MESSAGE = ENDOFTEXT+"""You are PipGPT, a large language model trained by OpenAI. Please return the pip install command to solve the user's problem.
Return only the command and nothing else."""
INSTALL_USER_MESSAGE = lambda package: f"""Write the windows pip3 command I can solve {package}. Please do not explain, return only the single command to install it."""
CONGNITIVE_SYSTEM_CALIBRATION_MESSAGE = """You are a helpful assistant. Please give your response to the user's goal."""
CONGNITIVE_USER_MESSAGE = """. Use a large language model with prompt engineering to help achieve this goal by importing the function LLM(prompt: str) -> str from HLVM.py. 
It is pre-defined in HLVM.py, so you do not need to define this function.
Don't forget to engineer the prompt to the LLM so it returns relevant answers."""
USER_MESSAGE = lambda goal: f"""Write python3 code so I can achieve my goal by running my code. Please do not explain, return only the code. My goal: [{goal}]. Don't forget to print the final result. """
CODE_USER_CALIBRATION_MESSAGE = """get information about canada"""
CODE_ASSISTANT_CALIBRATION_MESSAGE = """import wikipedia
# Set the language to English
wikipedia.set_lang("en")
# Get the page object for Canada (we never want auto_suggest)
canada_page = wikipedia.page("Canada", auto_suggest=False) 
# Print the summary of the page
print(canada_page.summary)
# Print the full content of the page
print(canada_page.content)"""
CODE_USER_CALIBRATION_MESSAGE2 = """make a shakespeare poem"""
CODE_ASSISTANT_CALIBRATION_MESSAGE2 = f"""import openai
openai.api_key = "your_openai_api_key_here"
prompt = "Write a Shakespearean poem: "
response = openai.Completion.create(
    engine="text-davinci-002",
    prompt=prompt,
    max_tokens=256,
    n=1,
    stop=None,
    temperature=0.7,
)
print(response.choices[0].text.strip())"""
CODE_USER_CALIBRATION_MESSAGE3 = """make my wallpaper a galaxy"""
CODE_ASSISTANT_CALIBRATION_MESSAGE3 = """import requests
import ctypes
import os
url = "https://api.unsplash.com/search/photos"
params = {
    "query": "galaxy",    # search for "galaxy"
    "orientation": "landscape",   # limit results to landscape orientation
    "client_id": "your_unsplash_access_key_here"   # Unsplash access key
}
response = requests.get(url, params=params)
# Get the URL of the first image in the results
image_url = response.json()["results"][0]["urls"]["regular"]
# Download the image and save it to a file
response = requests.get(image_url)
with open("galaxy.jpg", "wb") as f:
    f.write(response.content)
# Change it to a galaxy
ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath("galaxy.jpg"), 3)
# Print to confirm goal has been completed
print("Wallpaper changed to a galaxy.")"""