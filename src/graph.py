from nodes import *
from IPython.display import display, Image
from langchain_core.runnables.graph import MermaidDrawMethod
from langgraph.checkpoint.memory import MemorySaver

config = {"configurable": {"thread_id": "1"}}
set_variables()
def build_graph():
    builder=StateGraph(State)
    builder.add_node("summarize", summarize)
    builder.add_node("general_chat", message_general)
    builder.add_node("first_tool_call",first_tool_call)
    builder.add_node("list_tables",list_tables)
    builder.add_node("get_schema_tool",get_schema_tool_with_fallback)
    builder.add_node("model_get_schema",model_get_schema)
    builder.add_node("query_gen",query_gen_node)
    builder.add_node("correct_query",model_check_query)
    builder.add_node("tool_message",tool_message)
    builder.add_node("execute_query",execute_query)
    
    builder.add_edge(START, "summarize")
    builder.add_conditional_edges("summarize",route_to_research,{
        "first_tool_call":"first_tool_call",
        "general_chat":"general_chat"
    })
    builder.add_edge("first_tool_call", "list_tables")
    builder.add_edge("list_tables", "model_get_schema")
    builder.add_edge("model_get_schema", "get_schema_tool")
    builder.add_edge("get_schema_tool", "query_gen")
    builder.add_conditional_edges("query_gen", should_continue)
    builder.add_edge("correct_query", "execute_query")
    builder.add_edge("execute_query", "tool_message")
    builder.add_edge("tool_message", "query_gen")
    builder.add_edge("general_chat",END)
    memory = MemorySaver()
    graph=builder.compile(checkpointer=memory)
    return graph
graph=build_graph()
print(graph)
os.system("mkdir -p state_db && [ -f state_db/example.db ]")
while True:
    user_query=input("Enter your query: ")
    if user_query=="stop":
        break
    response=graph.invoke({"messages":[("user", user_query)]},config=config)
    print(response["messages"][-1].content)
