from openai import OpenAI
from colorama import Fore, Style
import os
import sys
from prompts import *
import subprocess
import io
import contextlib
import platform

MODEL = "gpt-4o-mini"

# Get LLM server credentials
API_KEY = os.environ.get("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1"
if not API_KEY:
    API_KEY = os.environ.get("OPENAI_API_KEY")
    API_URL = "https://api.openai.com/v1"
    if not API_KEY:
        print("Please set your OpenRouter or OpenAI API key as an environment variable.")
        sys.exit(1)

openai_client = OpenAI(
    api_key=API_KEY,
    base_url=API_URL
)

def print_formatted(text, color=Fore.WHITE):
    print(f"{Style.RESET_ALL}{color}{text}{Style.RESET_ALL}")

def clean_code(code):
    between_code_tags = code.split('```')[1] if '```' in code else code.strip('`')
    between_code_tags = between_code_tags.strip()
    if between_code_tags.startswith("python"):
        between_code_tags = between_code_tags[6:]
    return between_code_tags.strip()

def run_code(code):
    print_formatted("Running code:", Fore.YELLOW)
    print_formatted(code, Fore.CYAN)
    try:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            exec(code, globals())
        return True, output.getvalue()
    except Exception as e:
        return False, f"Error: {type(e).__name__}: {str(e)}"

def install_package(error):
    package = error.split("'")[-2]
    print_formatted(f"Installing {package}...", Fore.YELLOW)
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def run_shell():
    memory = [
        {"role": "system", "content": CODE_SYSTEM_CALIBRATION_MESSAGE},
    ]

    while True:
        user_input = input(f"{os.getcwd()} {Fore.CYAN}engshell>{Style.RESET_ALL} ")
        
        if user_input.lower() == 'clear':
            os.system("cls" if platform.system() == "Windows" else "clear")
            memory = memory[:1]
            continue

        memory.append({"role": "user", "content": USER_MESSAGE(user_input, os.getcwd())})

        while True:
            response = openai_client.chat.completions.create(model=MODEL, messages=memory)
            try:
                code = clean_code(response.choices[0].message.content)
            except Exception as e:
                print(f"Error ({e}): LLM response: {response}")
                exit()
            memory.append({"role": "assistant", "content": code})

            success, output = run_code(code)
            
            if success:
                print_formatted(output or "Code executed successfully.", Fore.GREEN)
                break
            elif "No module named" in output or "ImportError" in output:
                install_package(output)
            else:
                print_formatted(output, Fore.RED)
                memory.append({"role": "system", "content": DEBUG_MESSAGE(code, output)})

        memory.append({"role": "system", "content": output})

if __name__ == "__main__":
    if os.name == 'nt':
        os.system('')
    run_shell()
