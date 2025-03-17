FROM python:3.10

RUN mkdir /fast-api

COPY app.py graph.py nodes.py prompts.py set_api_keys.py states.py requirements.txt .env /fast-api

WORKDIR /fast-api

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt 
RUN pip install fastapi[standard]
ENTRYPOINT ["uvicorn","app:app", "--host", "0.0.0.0", "--port", "8000"]
