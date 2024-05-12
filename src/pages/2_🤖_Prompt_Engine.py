import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
import logging

load_dotenv()

client = OpenAI()

from PIL import Image

from utils import *

icon = Image.open(os.path.dirname(__file__) + '/../icon.png')

st.set_page_config(page_icon=icon)

st.markdown('# 🤖 Prompt Engine')

st.write("Prompt engineering is about giving correct instructions to GPT-4. The more precise the instructions, the better the results. The goal is to generate Manim code from a specific part of code. Than you can use the code to render the animation.")

prompt = st.text_area("Write your animation idea here. Use simple words.",
                      "Draw a blue circle and convert it to a red square")

openai_api_key = st.text_input(
    "Paste your own [Open API Key](https://platform.openai.com/account/api-keys)", value=os.getenv("OPENAI_API_KEY") or "", type="password")

openai_model = st.selectbox(
    "Select the GPT model. If you don't have access to GPT-4, select GPT-3.5-Turbo", ["GPT-3.5-Turbo", "GPT-4"])

generate_prompt = st.button(
    ":computer: Generate prompt :sparkles:", type="primary")

if generate_prompt:
  if not openai_api_key:
    st.error("Error: You need to provide your own Open API Key to use this feature.")
    st.stop()
  if not prompt:
    st.error("Error: You need to provide a prompt.")
    st.stop()

  response = client.chat.completions.create(model=openai_model.lower(),
  messages=[
      {"role": "system", "content": GPT_SYSTEM_INSTRUCTIONS},
      {"role": "user", "content": wrap_prompt(prompt)}
  ])

  content = response.choices[0].message.content
  logging.debug(content)

  code_response = extract_code(response.choices[0].message.content)
  logging.debug(code_response)

  code_response = extract_construct_code(code_response)
  logging.debug(code_response)

  code_response = remove_indentation(code_response)

  st.text_area(label="Generate text: ",
                value=content,
                key="content")

  st.text_area(label="Generate code: ",
               value=code_response,
               key="code_input")
