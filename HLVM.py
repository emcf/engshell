import openai
import time
from colorama import Fore, Style
import os
from prompts import SYSTEM_CALIBRATION_MESSAGE, CONGNITIVE_SYSTEM_CALIBRATION_MESSAGE, CONGNITIVE_USER_MESSAGE, USER_MESSAGE
from keys import OPENAI_KEY

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

def LLM(prompt):
    if len(prompt) > 10000: 
        print_err('context > 10000 chars')
        return ''
    time.sleep(1/API_CALLS_PER_MIN)
    moderation_resp = openai.Moderation.create(input=prompt)
    if moderation_resp.results[0].flagged:
        print_err('prompt flagged by moderation endpoint')
        return ''
    time.sleep(1/API_CALLS_PER_MIN)
    response = openai.ChatCompletion.create(
      #model="gpt-4",
      model="gpt-3.5-turbo-0301",
      messages=[
            {"role": "system", "content": CONGNITIVE_SYSTEM_CALIBRATION_MESSAGE},
            {"role": "user", "content": prompt},
        ],
      temperature = 0.0
    )
    response_content = response.choices[0].message.content
    return response_content

def LLM_code(prompt):
    openai.api_key = OPENAI_KEY
    if len(prompt) > 10000: 
        print_err('context > 10000 chars')
        return ''
    time.sleep(1/API_CALLS_PER_MIN)
    moderation_resp = openai.Moderation.create(input=prompt)
    if moderation_resp.results[0].flagged:
        print_err('flagged by moderation endpoint')
        return ''
    time.sleep(1/API_CALLS_PER_MIN)
    response = openai.ChatCompletion.create(
      model="gpt-4",
      messages=[
            {"role": "system", "content": SYSTEM_CALIBRATION_MESSAGE},
            {"role": "user", "content": prompt},
        ],
      temperature = 0.0
    )
    response_content = response.choices[0].message.content
    split_response_content = response_content.split('```')
    if len(split_response_content) > 1:
        response_content = split_response_content[1]
    for code_languge in ['python', 'bash']:
        if response_content[:len(code_languge)]==code_languge: response_content = response_content[len(code_languge)+1:] # remove python+newline blocks
    return response_content

def containerize_code(code_string, verbose):
    if verbose: print(code_string, end = '' if code_string[-1] == '\n' else '\n')
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
        return False, error_msg
    return True, None

def run_python(goal, debug = False, verbose = False):
    print_status("compiling...")
    returned_code = LLM_code(goal)
    success, output = containerize_code(returned_code, verbose)
    attempts = 0
    should_debug = debug and (attempts < MAX_DEBUG_ATTEMPTS) and (not success)
    should_retry = should_debug or ((output is not None) and any([(err in output) for err in IGNORE_ERRORS]))
    while should_retry:
        if should_debug:
            prompt = returned_code + '\n\n The previous code gives the error ' + output + ', given the following python code, rewrite the code with the error resolved:\n'
            print_status('debugging: ' + output)
            returned_code = LLM_code(prompt)
        success, output = containerize_code(returned_code, verbose)
        attempts += 1
        should_debug = debug and (attempts < MAX_DEBUG_ATTEMPTS) and (not success)
        should_retry = should_debug or any([(err in output) for err in IGNORE_ERRORS])
    if not success:
        print_err(f"exiting ({output})")
        return None
    return output

if __name__ == "__main__":
    #memory = [
    #    {"role": "system", "content": SYSTEM_CALIBRATION_MESSAGE},
    #    {"role": "user", "content": prompt}
    #]
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