import openai
import time
from colorama import Fore, Style
import os
from prompts import *
from keys import OPENAI_KEY
import subprocess
import io
import contextlib

openai.api_key = OPENAI_KEY
MAX_PROMPT = 4096
CONTEXT_LEFT, CONTEXT_RIGHT = '{', '}'
HLVM_PREVIX = Style.RESET_ALL + ' ' + Style.RESET_ALL + Fore.MAGENTA + "HLVM" + Style.RESET_ALL + '>'
API_CALLS_PER_MIN = 30
VERBOSE = False
MAX_DEBUG_ATTEMPTS = 2
IGNORE_ERRORS = ["The server had an error while processing your request. Sorry about that!"]
memory = []

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

def summarize(text):
    summarized = text
    raise NotImplementedError("summarize(text) not yet implemented")
    return summarized

def LLM(prompt, mode='text'):
    global memory
    if len(prompt) > MAX_PROMPT: 
        print_status('prompt too large, summarizing...')
        prompt = summarize(prompt)
    time.sleep(1.0/API_CALLS_PER_MIN)
    moderation_resp = openai.Moderation.create(input=prompt)
    if moderation_resp.results[0].flagged:
        raise ValueError(f'prompt ({prompt}) flagged by moderation endpoint')
    time.sleep(1.0/API_CALLS_PER_MIN)
    if mode == 'text':
        messages=[
            {"role": "system", "content": CONGNITIVE_SYSTEM_CALIBRATION_MESSAGE},
            {"role": "user", "content": prompt},
        ]
    elif mode == 'code':
        messages=memory+[{"role": "user", "content": prompt}]
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

def containerize_code(code_string):
    try:
        output_buffer = io.StringIO()
        with contextlib.redirect_stdout(output_buffer):
            exec(code_string,globals())
    except Exception as e:
        error_msg = str(e)
        return False, error_msg
    code_printout = output_buffer.getvalue()
    return True, code_printout

def run_python(goal, debug = False, showcode = False):
    print_status("compiling...")
    returned_code = LLM(goal, mode='code')
    if showcode: 
        print(returned_code, end = '' if returned_code[-1] == '\n' else '\n')
    print_status("running...")
    success, output = containerize_code(returned_code)
    attempts = 0
    should_debug = debug and (attempts < MAX_DEBUG_ATTEMPTS) and (not success)
    should_install = (output is not None) and ('No module named' in output)
    should_retry = should_debug or ((output is not None) and any([(err in output) for err in IGNORE_ERRORS]))
    while should_retry:
        if should_debug:
            if should_install:
                print_status('installing: ' + output)
                returned_command = LLM(prompt, mode='install')
                subprocess.run(returned_command, shell=True, capture_output=True, text=True)
            else:
                prompt = returned_code + '\n\n The previous code gives the error ' + output + ', given the following python code, rewrite the code with the error resolved:\n'
                print_status('debugging: ' + output)
                returned_code = LLM(prompt, mode='code')
                if showcode: 
                    print(returned_code, end = '' if returned_code[-1] == '\n' else '\n')
        success, output = containerize_code(returned_code)
        attempts += 1
        should_debug = debug and (attempts < MAX_DEBUG_ATTEMPTS) and (not success)
        should_retry = should_debug or any([(err in output) for err in IGNORE_ERRORS])
    if not success:
        print_err(f"exiting ({output})")
        return ''
    return output

def clear_memory():
    memory = [
            {"role": "system", "content": CODE_SYSTEM_CALIBRATION_MESSAGE},
            {"role": "user", "content": CODE_USER_CALIBRATION_MESSAGE},
            {"role": "assistant", "content": CODE_ASSISTANT_CALIBRATION_MESSAGE},
    ]

if __name__ == "__main__":
    if os.name == 'nt': os.system('')
    while user_input := input(os.getcwd() + HLVM_PREVIX):
        if user_input == 'refresh': 
            clear_memory()
        if '--llm' in user_input: user_input += CONGNITIVE_USER_MESSAGE
        debug = '--debug' in user_input
        showcode = '--showcode' in user_input
        user_input = user_input.replace('--llm','')
        user_input = user_input.replace('--debug','')
        user_input = user_input.replace('--showcode','')
        user_prompt = USER_MESSAGE(user_input)
        try:
            console_output = run_python(user_prompt, debug, showcode)
            if len(console_output) > MAX_PROMPT:
                print_status('output too large, summarizing...')
                console_output = summarize(console_output)
            print_success(console_output)
            memory.append({"role": "user", "content": user_prompt})
            memory.append({"role": "assistant", "content": console_output})
        except Exception as e:
            print_err(str(e))