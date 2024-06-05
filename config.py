from openai import OpenAI
import os
from dotenv import load_dotenv
from dataclasses import dataclass

#load_dotenv(find_dotenv())
load_dotenv('.env')
@dataclass(frozen=True)


class APIkeys:
    OpenAI_APIKEY: str = os.getenv('OpenAI_APIKEY')

completions_model = OpenAI(api_key=APIkeys.OpenAI_APIKEY)

#model = ChatOpenAI(model="llama3:latest", base_url="http://localhost:11434/v1", api_key="ollama")