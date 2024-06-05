from openai import OpenAI
import os
from dotenv import load_dotenv
from dataclasses import dataclass
import streamlit as st

#load_dotenv(find_dotenv())
load_dotenv('.env')
@dataclass(frozen=True)


class APIkeys:
    OpenAI_APIKEY: str = os.getenv('OpenAI_APIKEY')

completions_model = OpenAI(api_key=st.secrets["OpenAI_APIKEY"])

#model = ChatOpenAI(model="llama3:latest", base_url="http://localhost:11434/v1", api_key="ollama")