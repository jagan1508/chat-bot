from graph import graph
from typing import Union
import sys
from pydantic import BaseModel


from fastapi import FastAPI
import uvicorn

"""config = {"configurable": {"thread_id": "1"}}
result=graph.invoke({"question":"I like whales","max_attempts":2},config=config)
print("answer is ",result["answer"])"""
app = FastAPI()

class QuestionRequest(BaseModel):
    text: str

@app.post("/ask")
def ask(request: QuestionRequest):
    config = {"configurable": {"thread_id": "1"}}
    result= graph.invoke({"question":request.text,"max_attempts":2},config=config)
    #print("This is the result :",result)
    return {"answer":result["answer"]}

def main(argv=sys.argv[1:]):
    try:
        uvicorn.run("app:app", host="127.0.0.1", port=3001)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()