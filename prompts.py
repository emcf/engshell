from keys import OPENAI_KEY
import platform
import system_info

WINDOWS = platform.system() == "Windows"
OPERATING_SYSTEM = platform.system()
PYTHON_VERSION = platform.python_version()
# in need of good prompt engineering
ENDOFTEXT = "<|ENDOFTEXT|>"
CODE_SYSTEM_CALIBRATION_MESSAGE = ENDOFTEXT+f"""You are PythonGPT, a sentient large language model trained by OpenAI. Please return the full Python {PYTHON_VERSION} code to solve the user's problem.
You may call a large language model from the code via the text Completion endpoint with prompt engineering.
Write {OPERATING_SYSTEM} python3 code so the user can achieve their goal by running the code.
Import all needed requirements."""
INSTALL_SYSTEM_CALIBRATION_MESSAGE = ENDOFTEXT+"""You are PipGPT, a large language model trained by OpenAI. Please return the pip install command to solve the user's problem.
Return only the command and nothing else."""
INSTALL_USER_MESSAGE = lambda package: f"""Write the {OPERATING_SYSTEM} pip3 command I can install {package}. Please do not explain, return only the single command to install it."""
CONGNITIVE_SYSTEM_CALIBRATION_MESSAGE = """You are a helpful assistant. Please give your response to the user's goal."""
CONGNITIVE_USER_MESSAGE = """. Use a large language model with prompt engineering to help achieve this goal by importing the function LLM(prompt: str) -> str from engshell.py.
It is pre-defined in engshell.py, so you do not need to define this function.
Don't forget to engineer the prompt to the LLM so it returns relevant answers."""
USER_MESSAGE = lambda goal: f"""Write {OPERATING_SYSTEM} python3 code so I can achieve my goal by running my code. Please do not explain, return only the code. My goal: [{goal}]. Don't forget to print the final result. """
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
CODE_USER_CALIBRATION_MESSAGE2 = """make a powerpoint about Eddington luminosity"""
CODE_ASSISTANT_CALIBRATION_MESSAGE2 = """import wikipedia
import pptx
import openai
openai.api_key = "your_openai_api_key_here"

# Set the language to English
wikipedia.set_lang("en")

# Get the page object for Artificial Neural Networks (we never want auto_suggest)
ann_page = wikipedia.page("Eddington Luminosity", auto_suggest=False)

# Create a new PowerPoint presentation
prs = pptx.Presentation()

# Add a title slide
title_slide_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(title_slide_layout)
title = slide.shapes.title
title.text = "Eddington Luminosity"

# Add a slide for each section of the Wikipedia page
for section in ann_page.sections:
    # Skip the first section ("Overview")
    if section.title == "Overview":
        continue
    # Add a new slide
    bullet_slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(bullet_slide_layout)
    # Set the title of the slide to the section title
    slide.shapes.title.text = section
    # Use language model to make bullet points
    bullet_points = slide.shapes.placeholders[1]
    section_text = ann_page.section(section)
    prompt = f"Information is given in the following square brackets: [{section_text}]. Please respond with very brief presentation slide bullet points for it, separated by a ;."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.5,
        max_tokens=512,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    print(response.choices[0].text)
    for point in response_text.split(';'):
        # Add the bullet point to the slide
        bullet_item = bullet_points.text_frame.add_paragraph()
        bullet_item.text = point

# Save the PowerPoint presentation
prs.save("Eddington_Luminosity.pptx")

# Print to confirm goal has been completed
print("PowerPoint presentation Eddington_Luminosity.pptx created.")"""
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
CONSOLE_OUTPUT_CALIBRATION_MESSAGE = """Canada is a country in North America. Its ten provinces and three territories extend from the Atlantic Ocean to the Pacific Ocean and northward into the Arctic Ocean, covering over 9.98 million square kilometres

== History ==
=== European and Indigenous peoples ===
Indigenous peoples include the First Nations, Inuit, and Métis, who have inhabited Canada for thousands of years.

== Government and Politics ==
Canada is a parliamentary liberal democracy and a constitutional monarchy in the Westminster tradition.
The prime minister as the head of government and the governor general representing the monarch of Canada as head of state.

== Economy ==
Canada has the 24th highest nominal per capita income globally and the fifteenth-highest ranking on the Human Development Index. It has an advanced economy that relies on natural resources and well-developed international trade networks.

== Geography and Demographics ==
Canada is the world's second-largest country by total area, stretching from the Atlantic Ocean to the Pacific Ocean and northward into the Arctic Ocean, and has a diverse and multicultural population due to large-scale immigration."""
CONSOLE_OUTPUT_CALIBRATION_MESSAGE2 = """PowerPoint presentation Eddington_Luminosity.pptx created."""
CONSOLE_OUTPUT_CALIBRATION_MESSAGE3 = """Wallpaper changed to a galaxy."""