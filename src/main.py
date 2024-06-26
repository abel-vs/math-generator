import os
import subprocess
import streamlit as st
from manim import *
from openai import OpenAI
from PIL import Image

from utils import *

icon = Image.open(os.path.dirname(__file__) + '/icon.png')

st.set_page_config(
    page_title="Generative Manim",
    page_icon=icon,
)

styl = f"""
<style>
  textarea[aria-label="Code generated: "] {{
    font-family: 'Consolas', monospace !important;
  }}
</style>
"""
st.markdown(styl, unsafe_allow_html=True)

st.title(":art: Generative Manim")
st.write(":robot_face: Create beautiful and quick animations with GPT-4 and GPT-3.5 :sparkles:")

prompt = st.text_area("Write your animation idea here. Use simple words.",
                      "Draw a blue circle and convert it to a red square", max_chars=400,
                      key="prompt_input")

openai_api_key = ""

openai_model = st.selectbox(
    "Select the GPT model.", ["GPT-3.5-Turbo", "GPT-4"])

animation_model = st.selectbox(
    "Select the animation model.", ["Zero Shot Model", "LangGraph Model"])


generate_video = st.button(":computer: Animate :sparkles:", type="primary")
show_code = st.checkbox("Show generated code (that produces the animation)")

code_response = ""

if generate_video:

  if not openai_model:
    openai_model = "gpt-4"

  if not prompt:
    st.error("Error: Please write a prompt to generate the video.")
    st.stop()

  # If prompt is less than 10 characters, it will be rejected
  if len(prompt) < 10:
    st.error("Error: Your prompt is too short. Please write a longer prompt.")
    st.stop()

  # If prompt exceeds 240 characters, it will be truncated
  if len(prompt) > 400 and not openai_api_key:
    st.error("Error: Your prompt is longer than 400 characters. Please shorten it.")
    st.stop()

  # Prompt must be trimmed of spaces at the beginning and end
  prompt = prompt.strip()

  # Remove ", ', \ characters
  prompt = prompt.replace('"', '')
  prompt = prompt.replace("'", "")
  prompt = prompt.replace("\\", "")

  max_tokens = 1200 

  # If user has their own API key, use it
  if not openai_api_key:
    try:
      # If there is OPENAI_API_KEY in the environment variables, use it
      # Otherwise, use Streamlit secrets variable
      if os.environ["OPENAI_API_KEY"]:
        openai_api_key = os.environ["OPENAI_API_KEY"]
      else:
        openai_api_key = st.secrets["OPENAI_API_KEY"]
    except:
      st.error("Error: Sorry, I disabled my OpenAI API key (the budget is over). Please use your own API key and it will work perfectly. Otherwise, please send me a message on Twitter (@360macky)")
      st.stop()

  try:
    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model=openai_model.lower(),
        messages=[
            {"role": "system", "content": GPT_SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": wrap_prompt(prompt)}
        ]
    )
  except:
    if openai_model.lower() == "gpt-4":
      st.error(
          "Error: This is likely a rate limit error for GPT-4. Currently OpenAI accepts 25 requests every 3 hours for GPT-4. This means OpenAI will start rejecting some requests randomly. There are two solutions: Use GPT-3.5-Turbo, or use your own OpenAI API key.")
      st.stop()
    else:
      st.error(
          "Error: We couldn't generate the generated code. Please reload the page, or try again later")
      st.stop()

  code_response = extract_construct_code(
      extract_code(response.choices[0].message.content))

  # If code_response is empty, show an error
  if not code_response:
    st.error("Error: We couldn't generate the generated code. Please reload the page, or try again later")
    st.stop()

  if show_code:
    st.text_area(label="Code generated: ",
                 value=code_response,
                 key="code_input")

  if os.path.exists(os.path.dirname(__file__) + '/../../GenScene.py'):
    os.remove(os.path.dirname(__file__) + '/../../GenScene.py')

  if os.path.exists(os.path.dirname(__file__) + '/../../GenScene.mp4'):
    os.remove(os.path.dirname(__file__) + '/../../GenScene.mp4')

  try:
    with open("GenScene.py", "w") as f:
      f.write(create_file_content(code_response))
  except:
    st.error("Error: We couldn't create the generated code in the Python file. Please reload the page, or try again later")
    st.stop()

  COMMAND_TO_RENDER = "manim GenScene.py GenScene --format=mp4 --media_dir . --custom_folders video_dir"

  problem_to_render = False
  try:
    working_dir = os.path.dirname(__file__) + "/../"
    subprocess.run(COMMAND_TO_RENDER, check=True, cwd=working_dir, shell=True)
  except Exception as e:
    problem_to_render = True
    st.error(
        f"Error: Apparently GPT generated code that Manim (the render engine) can't process.\n\nThis is normal, since sometimes GPT can generate buggy code after all, and needs human intervention to fix it.\n\n**Ok. But what can you do now?**\n\nYou still can download the AI generated Python file with the button below (the one that failed to render) if you want to know what failed internally.\n\nYou can modify your prompt and try again. Remember, simpler and clearer prompts are better.\n\nYou can open an issue on the [GitHub Repository](https://github.com/360macky/generative-manim), attaching your prompt.")
  if not problem_to_render:
    try:
      video_file = open(os.path.dirname(__file__) + '/../GenScene.mp4', 'rb')
      video_bytes = video_file.read()
      st.video(video_bytes)
    except FileNotFoundError:
      st.error("Error: I couldn't find the generated video file. I know this is a bug and I'm working on it. Please reload the page.")
    except:
      st.error(
          "Error: Something went wrong showing your video. Please reload the page.")
  try:
    python_file = open(os.path.dirname(__file__) + '/../GenScene.py', 'rb')
    st.download_button("Download scene in Python",
                       python_file, "GenScene.py", "text/plain")
  except:
    st.error(
        "Error: Something went wrong finding the Python file. Please reload the page.")


st.write('Made with :heart: by [Marcelo](https://github.com/360macky).')
st.write('[Source code](https://github.com/360macky/generative-manim) - [Report a bug](https://github.com/360macky/generative-manim/issues/new) - [Twitter](https://twitter.com/360macky) - [OpenAI Profile](https://community.openai.com/u/360macky/summary)')
