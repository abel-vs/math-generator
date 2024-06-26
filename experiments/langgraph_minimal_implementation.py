# -*- coding: utf-8 -*-
"""Generative Manim LangGraph Implementation.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1YSO9TG2fJVVH4l7yTHE_V-v8VaDfpM2s

# Generative Manim LangGraph Implementation

Taking the example of [Code generation with flow](https://github.com/langchain-ai/langgraph/blob/main/examples/code_assistant/langgraph_code_assistant.ipynb?ref=blog.langchain.dev), we will implement a similar approach to generate code for Manim animations. So far, I think we would not need test validation, we can delay this step for later.
"""

"""## Extracting examples from Manim docs"""
# Load .env
from dotenv import load_dotenv
load_dotenv()

import os
from bs4 import BeautifulSoup as Soup
from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader

# Manim Examples docs
url = "https://docs.manim.community/en/stable/examples.html"
loader = RecursiveUrlLoader(
    url=url, max_depth=20, extractor=lambda x: Soup(x, "html.parser").text
)
docs = loader.load()

# Sort the list based on the URLs and get the text
d_sorted = sorted(docs, key=lambda x: x.metadata["source"])
d_reversed = list(reversed(d_sorted))
concatenated_content = "\n\n\n --- \n\n\n".join(
    [doc.page_content for doc in d_reversed]
)

"""## LLM Solution"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
import os

# Initial configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
llm = ChatOpenAI(temperature=0, model="gpt-4-0125-preview", openai_api_key=OPENAI_API_KEY)

# Message template for the LLM
code_gen_prompt = ChatPromptTemplate.from_messages(
    [("system", "You are a coding assistant with expertise in Manim, the Graphical Animation Library. Please generate code based on the user's request."),
     ("placeholder", "{messages}")]
)

# Data model for structured output
class Code(BaseModel):
    prefix: str = Field(description="Description of the problem and approach")
    imports: str = Field(description="Code block import statements")
    code: str = Field(description="Executable code block")

# Function to handle errors
def handle_errors(inputs):
    error = inputs["error"]
    messages = inputs["messages"]
    messages += [
        ("assistant", f"Please correct the following error: {error}")
    ]
    return {"messages": messages, "context": inputs["context"]}

# Fallback chain for error handling
fallback_chain = handle_errors | (code_gen_prompt | llm.with_structured_output(Code))

# Retry configuration
N = 3  # Number of retries
code_gen_chain_with_retry = (code_gen_prompt | llm.with_structured_output(Code)).with_fallbacks(fallbacks=[fallback_chain] * N, exception_key="error")

# Function to parse the output
def parse_output(solution: Code):
    # Ensure the solution is an instance of Code and access its attributes directly
    if isinstance(solution, Code):
        return {
            "prefix": solution.prefix,
            "imports": solution.imports,
            "code": solution.code
        }
    else:
        raise TypeError("Expected a Code instance")

# Final chain with retries and parsing
code_gen_chain = code_gen_chain_with_retry | parse_output

# Using the chain to generate code
question = "Draw three red circles"
solution = code_gen_chain.invoke({"context": concatenated_content, "messages": [("user", question)]})
print(solution)
