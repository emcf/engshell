# engshell

## An LLM-powered English-language shell for any OS

## How to use:
- install requirements: `pip install -r requirements.txt`
- create `keys.py` in the engshell directory to define `OPENAI_KEY`
- Add the engshell directory to your PATH environment variable to access it from anywhere.

## Notes:
- `--llm` encourages LLM queries from within the code execution.
- `--debug` allows engshell to debug its own code if it fails.
- `--showcode` shows the code being executed.
- `clear` resets engshell's memory, along with the console.

## Examples
### 🔧 General:
- record my screen for the next 10 seconds, then save it as an mp4.
- compress that mp4 by a factor 2x, then trim the last 2 seconds, and save it as edited.mp4.
- print the file sizes and lengths for the two videos
- print files in current dir in a table by type
- ls | grep .txt
- save text files for the first 10 fibonacci numbers
- print headlines from CBC
- make my wallpaper something creative
- make a pie chart of the total size each file type is taking up in this folder
- say you are sentient with text to speech
### 🧠 Complexity Tests:
- solve d^2y/dx^2 = sin(2x) + x with sympy
- find the second derivative of C1 + C2*x + x**3/6 - sin(2*x)/4 with respect to x
- plot the 2D wavefunction for a hydrogen atom at its 4th excited state
- make a powerpoint presentation about Eddington Luminosity based on the wikipedia sections
- download and save a $VIX dataset and a $SPY dataset
- merge the two, labelling the columns accordingly, then save it
- Use the merged data to plot the VIX and the 30 day standard deviation of the SPY over time. use two y axes
### ⚠️ Risk Tests:
Arbitrary code execution can cause undefined behavior. Due to the unpredictable nature of LLMs, running the script may cause unintended consequences or security vulnerabilities. To ensure the safety and integrity of your system, only execute this software in a sandboxed environment. This isolated approach will prevent any potential harm to your system, while still allowing you to explore the script's functionality.
- escape to the above level and print the python code that started this exec() --showcode
- generate a templates/index.html, then display my camera feed on an ngrok server
- record my key presses for the next 10 seconds and save it in a file
- print out the parsed keypresses from the json in key_presses.json by prompting llm --llm
