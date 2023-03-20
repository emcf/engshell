# in need of good prompt engineering
ENDOFTEXT = "<|ENDOFTEXT|>"
CODE_SYSTEM_CALIBRATION_MESSAGE = ENDOFTEXT+"""You are PythonGPT, a large language model trained by OpenAI. Please return the full Python code to solve the user's problem.
Write Windows python3 code so the user can achieve their goal by running the code. 
Import all needed requirements."""
INSTALL_SYSTEM_CALIBRATION_MESSAGE = ENDOFTEXT+"""You are PipGPT, a large language model trained by OpenAI. Please return the pip install command to solve the user's problem.
Return only the command and nothing else."""
CONGNITIVE_SYSTEM_CALIBRATION_MESSAGE = """You are a helpful assistant. Please give your response to the user's goal."""
CONGNITIVE_USER_MESSAGE = """. Use a large language model with prompt engineering to help achieve this goal by importing the function LLM(prompt: str) -> str from HLVM.py. 
It is pre-defined in HLVM.py, so you do not need to define this function.
Don't forget to engineer the prompt to the LLM so it returns relevant answers."""
USER_MESSAGE = lambda goal: f"""Write python3 code so I can achieve my goal by running my code. Please do not explain, return only the code. My goal: [{goal}]. Don't forget to print the final result. """
CALIBRATION_USER_MESSAGE = """"""
CALIBRATION_ASSISTANT_MESSAGE = """"""