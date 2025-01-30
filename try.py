from langchain_nvidia_ai_endpoints import ChatNVIDIA


model = ChatNVIDIA(model="meta/llama2-70b")
response = model.invoke("Hello")