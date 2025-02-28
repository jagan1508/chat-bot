from graph import graph
from typing import Union

from fastapi import FastAPI
import uvicorn

app = FastAPI()


#@app.get("/")
#def read_root():
#    return {"Hello": "World"}


@app.post("/ask")
def ask(text: str):
    config = {"configurable": {"thread_id": "1"}}
    result= graph.invoke({"messages":[("user", text)]},config=config)
    return {"answer":result["messages"][-1].content}
##if __name__ == '__main__':
##   uvicorn.run(app, host='127.0.0.1', port=8000)
