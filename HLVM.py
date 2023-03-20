import openai
import time
from colorama import Fore, Style
import os
from prompts import *
from keys import OPENAI_KEY
import subprocess

openai.api_key = OPENAI_KEY
CONTEXT_LEFT, CONTEXT_RIGHT = '{', '}'
HLVM_PREVIX = Style.RESET_ALL + "<HLVM> "
API_CALLS_PER_MIN = 30
VERBOSE = False
MAX_DEBUG_ATTEMPTS = 2
IGNORE_ERRORS = ["The server had an error while processing your request. Sorry about that!"]

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

def clean_code_string(response_content):
    split_response_content = response_content.split('```')
    if len(split_response_content) > 1:
        response_content = split_response_content[1]
    for code_languge in ['python', 'bash']:
        if response_content[:len(code_languge)]==code_languge: response_content = response_content[len(code_languge)+1:] # remove python+newline blocks
    return response_content    

def LLM(prompt, mode='text'):
    if len(prompt) > 10000: raise ValueError('context > 10000 chars')
    time.sleep(1.0/API_CALLS_PER_MIN)
    moderation_resp = openai.Moderation.create(input=prompt)
    if moderation_resp.results[0].flagged:
        raise ValueError('prompt flagged by moderation endpoint')
    time.sleep(1.0/API_CALLS_PER_MIN)
    if mode == 'text':
        messages=[
            {"role": "system", "content": CONGNITIVE_SYSTEM_CALIBRATION_MESSAGE},
            {"role": "user", "content": prompt},
        ]
    elif mode == 'code':
        messages=[
            {"role": "system", "content": CODE_SYSTEM_CALIBRATION_MESSAGE},
            {"role": "user", "content": prompt},
        ]
    elif mode == 'install':
        messages=[
            {"role": "system", "content": INSTALL_SYSTEM_CALIBRATION_MESSAGE},
            {"role": "user", "content": prompt},
        ]
    response = openai.ChatCompletion.create(
      #model="gpt-4",
      model="gpt-3.5-turbo-0301",
      messages=messages,
      temperature = 0.0
    )
    response_content = response.choices[0].message.content
    if mode == 'code': response_content = clean_code_string(response_content)
    return response_content

def containerize_code(code_string, verbose):
    if verbose: print(code_string, end = '' if code_string[-1] == '\n' else '\n')
    print_status("running...")
    try:
        print(Style.RESET_ALL + Fore.GREEN, end="")
        exec(code_string,globals())
    except Exception as e:
        error_msg = str(e)
        return False, error_msg
    return True, None

def run_python(goal, debug = False, verbose = False):
    print_status("compiling...")
    returned_code = LLM(goal, mode='code')
    success, output = containerize_code(returned_code, verbose)
    attempts = 0
    should_debug = debug and (attempts < MAX_DEBUG_ATTEMPTS) and (not success)
    should_install = (output is not None) and ('No module named' in output)
    should_retry = should_debug or ((output is not None) and any([(err in output) for err in IGNORE_ERRORS]))
    while should_retry:
        if should_debug:
            if should_install:
                print_status('installing: ' + output)
                returned_command = LLM(prompt, mode='install')
                result = subprocess.run(returned_command, shell=True, capture_output=True, text=True)
                print(result)
            else:
                prompt = returned_code + '\n\n The previous code gives the error ' + output + ', given the following python code, rewrite the code with the error resolved:\n'
                print_status('debugging: ' + output)
                returned_code = LLM(prompt, mode='code')
        success, output = containerize_code(returned_code, verbose)
        attempts += 1
        should_debug = debug and (attempts < MAX_DEBUG_ATTEMPTS) and (not success)
        should_retry = should_debug or any([(err in output) for err in IGNORE_ERRORS])
    if not success:
        print_err(f"exiting ({output})")
        return None
    return output

if __name__ == "__main__":
    memory = [

    ]
    if os.name == 'nt': os.system('')
    while user_input:=input(HLVM_PREVIX):
        if '--cognitive' in user_input: user_input += CONGNITIVE_USER_MESSAGE
        debug = '--debug' in user_input
        verbose = '--showcode' in user_input
        user_input = user_input.replace('--cognitive','')
        user_input = user_input.replace('--debug','')
        user_input = user_input.replace('--showcode','')
        #try:
        run_python(USER_MESSAGE(user_input), debug, verbose)
        #except Exception as e:
        #    print_err(str(e))