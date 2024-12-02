import platform
import getpass

USERNAME = getpass.getuser()
OPERATING_SYSTEM = platform.system()
PYTHON_VERSION = platform.python_version()

# in need of good prompt engineering
OPENROUTER_DOCS = """<Openrouter Docs>
from openai import OpenAI # You MUST import OpenAI from openai. There is no OpenRouter package.

# Always initialize the OpenAI client using OpenRouter credentials
# NEVER use standard OpenAI.
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"],
)
# Messages must be in OpenAI format
# You must always specify in the prompt that the response should be in JSON format,
# and always include the desired response structure and key names in the prompt.
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "Instructional prompt here... Always reply in valid JSON format with the following structure: ..."
            },
            {
                "type": "image_url",
                "image_url": "data:image/jpeg;base64,..."
            }
        ]
    },
]
# Always call the OpenRouter API with these exact parameters
response = openrouter_client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=messages,
    response_format={"type": "json_object"}, # Only include this if you need a structured output. If you do include this, you MUST include "Always reply in valid JSON format with the following structure:" in the prompt text or it will throw an error.
    temperature=0,
)
# Get text from response
response_text = response.choices[0].message.content
# Load it into a dictionary
try:
    response_dict = json.loads(response_text)
except:
    response_dict = {"error": f"Failed to decode response: {response_text}"}
</Openrouter Docs>"""

CODE_SYSTEM_CALIBRATION_MESSAGE = f"""You are PythonGPT. Please write a full {OPERATING_SYSTEM} Python {PYTHON_VERSION} script, so the user (username: {USERNAME}) can run it to solve their problem. Return the full code in ``` blocks. Never give explanations. Do not return any text that is not Python code.
Import all needed requirements at the top of the script.
Always use tqdm to show progress for any loops.
If the task involves using a large language model, you can use OpenRouter API.
{OPENROUTER_DOCS}
Return the full code in ``` blocks. Never give explanations. Do not return any text that is not Python code."""

DEBUG_SYSTEM_CALIBRATION_MESSAGE = f"""You are PythonGPT, a large language model trained by OpenAI. Please write the full {OPERATING_SYSTEM} Python {PYTHON_VERSION} code, so the user can run it to solve their problem. For example, if the error was "No such file or directory", then you would download the necessary file or create the directory. Explain your reasoning in plain english, then provide the corrected code. Give the entire code all in one ``` block."""

def USER_MESSAGE(goal, current_dir): 
    return f"""(USER: {USERNAME})
(DIRECTORY: {current_dir})
Write {OPERATING_SYSTEM} python {PYTHON_VERSION} code so I can achieve my goal by running my code. Do not explain anything. Return only the code. My goal: [{goal}]. Don't forget to print the final result. """

def DEBUG_MESSAGE(code, error):
    return f"""```python
{code}
```
The above code returns the error "{error}". Please briefly explain in plain English why the error is happening, then write the corrected code in a code box.""" # CoT prompting improves debugging