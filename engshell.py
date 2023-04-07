import openai
import time
from colorama import Fore, Style
import os
import sys
from prompts import *
from keys import *
import subprocess
import io
import contextlib
import platform

openai.api_key = OPENAI_KEY
MAX_PROMPT = 20480
CONTEXT_LEFT, CONTEXT_RIGHT = '{', '}'
engshell_PREVIX = lambda: Style.RESET_ALL + os.getcwd() + ' ' + Style.RESET_ALL + Fore.MAGENTA + "engshell" + Style.RESET_ALL + '>'
API_CALLS_PER_MIN = 50
VERBOSE = False
MAX_DEBUG_ATTEMPTS = 2
RETRY_ERRORS = ["The server had an error while processing your request. Sorry about that!"]
memory = []

def print_console_prompt():
    print(engshell_PREVIX(), end="")

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
    return response_content.replace('`','')

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
            {"role": "system", "content": LLM_SYSTEM_CALIBRATION_MESSAGE},
            {"role": "user", "content": prompt},
        ]
    elif mode == 'code':
        messages=memory
    elif mode == 'debug':
        messages=[
            {"role": "system", "content": DEBUG_SYSTEM_CALIBRATION_MESSAGE},
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

def containerize_code(code_string):
    code_string = code_string.replace('your_openai_api_key_here', OPENAI_KEY)
    # uncomment this if you wish to easily use photos from Unsplash API
    # code_string = code_string.replace('your_unsplash_access_key_here', UNSPLASH_ACCESS_KEY)
    try:
        output_buffer = io.StringIO()
        with contextlib.redirect_stdout(output_buffer):
            exec(code_string,globals())
    except Exception as e:
        error_msg = str(e)
        print('got error message:', error_msg)
        return False, error_msg
    code_printout = output_buffer.getvalue()
    return True, code_printout

def run_python(returned_code, debug = False, showcode = False):
    print_status("compiling...")
    if showcode: 
        print(returned_code, end = '' if returned_code[-1] == '\n' else '\n')
    print_status("running...")
    returned_code = clean_code_string(returned_code)
    success, output = containerize_code(returned_code)
    attempts = 0
    should_debug = debug and (attempts < MAX_DEBUG_ATTEMPTS) and (not success)
    should_install = (output is not None) and ('No module named' in output)
    should_retry = should_debug or should_install or ((output is not None) and any([(err in output) for err in RETRY_ERRORS]))
    while should_retry:
        if should_install:
            print_status('installing: ' + output)
            prompt = INSTALL_USER_MESSAGE(output)
            returned_command = LLM(prompt, mode='install')
            os.system(returned_command)
        elif should_debug:
            print_status('debugging: ' + output)
            prompt = DEBUG_MESSAGE(returned_code, output)
            returned_code = LLM(prompt, mode='debug')
            if showcode: 
                print(returned_code, end = '' if returned_code[-1] == '\n' else '\n')
        returned_code = clean_code_string(returned_code)
        success, output = containerize_code(returned_code)
        attempts += 1
        should_debug = debug and (attempts < MAX_DEBUG_ATTEMPTS) and (not success)
        should_retry = should_debug or any([(err in output) for err in RETRY_ERRORS])
    if not success:
        raise ValueError(f"failed ({output})")
    return output

def clear_memory():
    global memory
    memory = [
            {"role": "system", "content": CODE_SYSTEM_CALIBRATION_MESSAGE},
            {"role": "user", "content": CODE_USER_CALIBRATION_MESSAGE},
            {"role": "assistant", "content": CODE_ASSISTANT_CALIBRATION_MESSAGE},
            {"role": "system", "content": CONSOLE_OUTPUT_CALIBRATION_MESSAGE},
            # uncomment these if you wish to easily use photos from Unsplash API
            #{"role": "user", "content": CODE_USER_CALIBRATION_MESSAGE3},
            #{"role": "assistant", "content": CODE_ASSISTANT_CALIBRATION_MESSAGE3},
            #{"role": "system", "content": CONSOLE_OUTPUT_CALIBRATION_MESSAGE3},
    ]

if __name__ == "__main__":
    if os.name == 'nt': os.system('')
    if '--showcode' in sys.argv:
        print("showcode argument set to enabled")
        always_showcode = True
    else:
        always_showcode = False
    if '--debug' in sys.argv:
        print("debug argument set to enabled")
        always_debug = True
    else:
        always_debug = False
    if '--llm' in sys.argv:
        print("llm argument set to enabled")
        always_llm = True
    else:
        always_llm = False
    clear_memory()
    while user_input := input(engshell_PREVIX()):
        if user_input == 'clear':
            clear_memory()
            os.system("cls" if platform.system() == "Windows" else "clear")
            continue
        if ('--llm' in user_input) or always_llm: user_input += CONGNITIVE_USER_MESSAGE
        debug = ('--debug' in user_input) or always_debug
        showcode = ('--showcode' in user_input) or always_showcode
        user_input = user_input.replace('--llm','')
        user_input = user_input.replace('--debug','')
        user_input = user_input.replace('--showcode','')
        user_prompt = USER_MESSAGE(user_input)
        memory.append({"role": "user", "content": user_prompt})
        run_code = True
        while run_code:
            returned_code = LLM(user_prompt, mode='code')
            memory.append({"role": "assistant", "content": returned_code})
            try:
                console_output = run_python(returned_code, debug, showcode)
                #if len(console_output) > MAX_PROMPT:
                #    print_status('output too large, summarizing...')
                #    console_output = summarize(console_output)
                if console_output.strip() == '': console_output = 'done executing.'
                print_success(console_output)
                run_code = False
            except Exception as e:
                error_message = str(e)
                console_output = error_message
                run_code = any([err in error_message for err in RETRY_ERRORS])
            if len(console_output) < MAX_PROMPT:
                memory.append({"role": "system", "content": console_output})