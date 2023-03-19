import openai
import time
import traceback
import sys
from colorama import Fore, Style
import os
from prompts import CODE_SYSTEM_MESSAGE, CONGNITIVE_SYSTEM_MESSAGE, CONGNITIVE_USER_MESSAGE, CODE_PROMPT_PREFIX
from keys import OPENAI_KEY
openai.api_key = OPENAI_KEY
CONTEXT_LEFT, CONTEXT_RIGHT = '{', '}'
HLVM_PREVIX = Style.RESET_ALL + "<HLVM> "
API_CALLS_PER_MIN = 40
DEBUG = False

def print_console_prompt():
    print(HLVM_PREVIX, end="")

def print_status(status):
    print_console_prompt()
    print(Style.RESET_ALL + Fore.YELLOW + status + Style.RESET_ALL)

def print_success(status):
    print_console_prompt()
    print(Style.RESET_ALL + Fore.GREEN + status + Style.RESET_ALL)

def print_err(status):
    print_console_prompt()
    print(Style.RESET_ALL + Fore.RED + status + Style.RESET_ALL)

def prompt_LLM(prompt, code = False):
    openai.api_key = OPENAI_KEY
    if len(prompt) > 10000: 
        print_err('context > 10000 chars')
        return ''
    time.sleep(1/API_CALLS_PER_MIN)
    response = openai.ChatCompletion.create(
      model="gpt-4",
      messages=[
            {"role": "system", "content": CODE_SYSTEM_MESSAGE if code else CONGNITIVE_SYSTEM_MESSAGE},
            {"role": "user", "content": prompt},
        ],
      temperature = 0.0
    )
    response_content = response.choices[0].message.content
    if code:
        split_response_content = response_content.split('```')
        if len(split_response_content) > 1:
            response_content = split_response_content[1]
        for code_languge in ['python', 'bash']:
            if response_content[:len(code_languge)]==code_languge: response_content = response_content[len(code_languge)+1:] # remove python+newline blocks
    return response_content

def containerize_code(code_string):
    print_status("running...")
    try:
        print(Style.RESET_ALL + Fore.GREEN, end="")
        exec(code_string,globals())
    except Exception as e:
        # Experimental: give entire traceback to LLM
        #tb_str = traceback.format_exception(*sys.exc_info())
        #for tb in enumerate(reversed(tb_str)):
        #    if "line" in tb:
        #        tb = tb.strip()
        #        line_num = int(tb.split(",")[1].split(" ")[-1])
        #        break
        error_msg = str(e)
        print_status('debugging: ' + error_msg)
        return False, error_msg
    return True, None

def run_python(goal):
    print_status("compiling...")
    returned_code = prompt_LLM(goal, code = True)
    if DEBUG: print(returned_code)
    success, output = containerize_code(returned_code)
    tries = 0
    max_tries = 2
    while tries < max_tries and not success:
        prompt = returned_code + '\n\n The previous code gives the error ' + output + ', given the following python code, rewrite the code with the error resolved:\n'
        print_status('compiling...')
        returned_code = prompt_LLM(prompt, code = True)
        success, output = containerize_code(returned_code)
        tries += 1
    if not success:
        print_err(f"exiting, failed after debugging {max_tries} times.")
        return None
    return output

if __name__ == "__main__":
    if os.name == 'nt': os.system('')
    while user_input:=input(HLVM_PREVIX):
        if '--cognitive' in user_input:
            user_input += '. ' + CONGNITIVE_USER_MESSAGE
            user_input = user_input.replace('--cognitive','')
        try:
            run_python(CODE_PROMPT_PREFIX(user_input))
        except Exception as e:
            print_err(str(e))