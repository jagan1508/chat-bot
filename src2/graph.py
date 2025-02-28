from nodes import *
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

def build_graph():
    builder= StateGraph(OverallState, input=InputState, output=OutputState)
    builder.add_node(select_relevant_schemas)
    builder.add_node(generate_query)
    builder.add_node(execute_query)
    builder.add_node(generate_answer)
    builder.add_node(general_chat)

    builder.add_conditional_edges(START,categorise)
    builder.add_conditional_edges("select_relevant_schemas",check_question)
    builder.add_edge("generate_query","execute_query")
    builder.add_conditional_edges("execute_query",router)
    builder.add_edge("generate_answer",END)
    builder.add_edge("general_chat",END)

    memory=MemorySaver()
    graph= builder.compile(checkpointer=memory)

    return graph

graph=build_graph()