import getpass
import os

from dotenv import load_dotenv

load_dotenv()


import getpass
import os

if not os.environ.get("GROQ_API_KEY"):
  os.environ["GROQ_API_KEY"] = getpass.getpass("Enter API key for Groq: ")

from langchain_groq import ChatGroq
llm = ChatGroq(model="llama3-8b-8192",temperature=0)
messages = [
    (
        "system",
        "You are a helpful assistant that translates English to French. Translate the user sentence.",
    ),
    ("human", "I love programming."),
]

response=llm.invoke(messages)
print(response.content)