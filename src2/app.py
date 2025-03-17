from graph import graph
from typing import Union
import sys
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI
import uvicorn

"""config = {"configurable": {"thread_id": "1"}}
result=graph.invoke({"question":"I like whales","max_attempts":2},config=config)
print("answer is ",result["answer"])"""
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

class QuestionRequest(BaseModel):
    text: str

@app.post("/ask")
def ask(request: QuestionRequest):
    print(request.text)
    config = {"configurable": {"thread_id": "1"}}
    result= graph.invoke({"question":request.text,"max_attempts":2},config=config)
    if result["answer"]:
        return {"answer":result["answer"]}
    else:
        return {"answer": result["error_message"]}



def main(argv=sys.argv[1:]):
    try:
        uvicorn.run("app:app", host="127.0.0.1", port=8000)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()