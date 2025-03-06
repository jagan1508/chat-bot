from graph import graph
from typing import Union

from fastapi import FastAPI
import uvicorn

"""config = {"configurable": {"thread_id": "1"}}
result=graph.invoke({"question":"I like whales","max_attempts":2},config=config)
print("answer is ",result["answer"])"""
app = FastAPI()

@app.post("/ask")
def ask(text: str):
    config = {"configurable": {"thread_id": "1"}}
    result= graph.invoke({"question":text,"max_attempts":2},config=config)
    #print("This is the result :",result)
    return result["answer"]