from set_api_keys import *
from langchain_community.utilities import SQLDatabase
from langchain_community.utilities import SQLDatabase
from typing import Any
from langchain_core.runnables import RunnableWithFallbacks, RunnableLambda
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode
from langchain_community.utilities import SQLDatabase
import pymysql
from langchain_core.tools import tool
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from prompts import *
from typing import Annotated, Literal
from langchain_core.messages import AIMessage,HumanMessage,RemoveMessage,SystemMessage
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langgraph.graph import START,END,StateGraph, MessagesState

config = {"configurable": {"thread_id": "1"}}
class State(MessagesState):
    summary: str
    pass

def set_variables():
    set_env("GROQ_API_KEY")
    set_env("LANGCHAIN_API_KEY")
    os.environ["LANGCHAIN_TRACING_V2"]="true"
    os.environ["LANGCHAIN_PROJECT"]="sql-llm-agent-tracker"


def load_database(username: str, password: str, host:str, database:str):
    db = SQLDatabase.from_uri(f"mysql+pymysql://{username}:{password}@{host}/{database}",sample_rows_in_table_info = 3)
    #print(db.dialect)
    #print(db.get_usable_table_names())
    return db

def create_tool_node_with_fallback(tools:list)-> RunnableWithFallbacks[Any,dict]:
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)],exception_key="error"
    )
def handle_tool_error(state)->dict:
    error=state.get("error")
    tool_calls=state["messages"][-1].tool_calls
    return {
        "messages":[ToolMessage(
            content=f"Error:{repr(error)}\n Fix your code and try again. ",
            tool_call_id=tc["id"],
        )
         for tc in tool_calls          
        ]
    }

@tool
def db_query_tool(query:str)->str:
    """Executes an sql query against the database and gets back 
    the result. If query is not correct an error message is returned.

    Args:
        query (str): A valid sql query string

    Returns:
        str: The result of the query if present or an error message
    """
    try:
        result=db.run_no_throw(query)
        if not result:
            return "Error: Query failed to return anything. Try again."
        return result
    except Exception as e:
        return f"Error: {str(e)}. Please check your query again."

def summarize(state: State):
    if len(state["messages"]) >5:
        summary = state.get("summary", "")
        if summary:
            # A summary already exists
            summary_message = (
                f"""This is summary of the conversation to date: {summary}\n\n
                Please extend the existing conversation summary by:

                1. PRIORITY ELEMENTS (Must Preserve):
                - Complete SQL queries exactly as generated
                - Original natural language requests that led to queries
                - Table schemas and database context
                - Most recent conversation elements

                2. FORMATTING RULES:
                - If total length exceeds 500 words:
                * Prioritize most recent exchanges
                * Maintain all SQL queries in full
                * Condense older context while preserving key details
                * Use bullet points for clarity

                3. CONTENT GUIDELINES:
                - Include only explicitly stated information
                - No assumptions or inferred details
                - Maintain chronological flow
                - Highlight query-context relationships

                4. STRUCTURE:
                - Recent Information (Latest exchanges)
                - SQL Queries (With associated context)
                - Schema Details (As referenced)
                - Earlier Context (Condensed if needed)

                Note: Focus on technical accuracy and query preservation while maintaining a clear, concise narrative flow."""
            )
            
        else:
            summary_message = """Generate a summary of the conversation above, focusing on the process of converting a natural language input into 
            an SQL query. Retain the exact SQL query that was generated without any modifications. 
            Additionally, preserve the context in which the query was created, 
            including the original natural language request and the table schema used. Do not add or 
            assume any information beyond what was explicitly stated in the conversation."""

        # Add prompt to our history
        model=ChatGroq(model="mixtral-8x7b-32768")
        messages = state["messages"][:-1] + [HumanMessage(content=summary_message)]
        response = model.invoke(messages)
        if len(state["messages"])>5:
            delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
        else:
            delete_messages-state["messages"]
        return {"summary": response.content, "messages": delete_messages}
    return state

def first_tool_call(state:State) ->dict[str,list[AIMessage]]:
    tool_call={"name":"sql_db_list_tables",
               "args":{},
               "id":"tool_abcd123"}
    return {"messages":[AIMessage(
        content='',
        tool_calls=[tool_call])]}

def model_check_query(state:State)->dict[str,list[AIMessage]]:
    return {"messages": [query_checker.invoke({"messages": [state["messages"][-1]]})]}

def model_get_schema(state:State):
    model_get_schema=schema_prompt|ChatGroq(model="llama-3.3-70b-versatile",temperature=0).bind_tools([get_schema_tool],tool_choice="required")
    return {
        "messages":[model_get_schema.invoke({"messages":state["messages"]})]
    }
def query_gen_node(state:State):
    message=query_gen_chain.invoke(state,config=config)
    return {"messages":[message]}

def should_continue(state:State)-> Literal[END,"correct_query","query_gen"]:
    messages=state["messages"]
    last_message=messages[-1]
    if last_message.content.startswith("Answer:"):
        return END
    if last_message.content.startswith("Error:"):
        return "query_gen"
    else:
        return "correct_query"

def route_to_research(state:State):
    initial_message = state["messages"]

    router = category_deciding_llm.invoke(input={"messages": initial_message} ,config=config)
    #
    if router.content== 'sql':
        return "first_tool_call"
    elif router.content == 'message':
        return "general_chat"

def tool_message(state:State):
    message=state["messages"]
    flag_message="This is the result of the query from the database :" + (message[-1].content)
    messages=[SystemMessage(
        content=flag_message
    )]
    return {"messages": messages}

def message_general(state:State):
    messages=state["messages"]
    answer=general_task_llm.invoke({"messages":messages},config=config)
    return {"messages": [answer]}

db=load_database(username="root",
                    password="jagan2911",
                    host="localhost",
                    database="jagandb")

toolkit= SQLDatabaseToolkit(db=db, llm=ChatGroq(model="llama-3.3-70b-versatile"))
tools= toolkit.get_tools()
list_tables_tool=next(tool for tool in tools if tool.name=="sql_db_list_tables")    
get_schema_tool=next(tool for tool in tools if tool.name=="sql_db_schema")

query_check_prompt=ChatPromptTemplate.from_messages([("system",QUERY_CHECK_INSTRUCTION),("placeholder","{messages}")])
query_checker=query_check_prompt | ChatGroq(model="llama-3.3-70b-versatile",temperature=0).bind_tools([db_query_tool],tool_choice="required")

query_gen_prompt=ChatPromptTemplate.from_messages([("system",QUERY_GEN_INSTRUCTION),("placeholder","{messages}")])
query_gen_chain=query_gen_prompt | ChatGroq(model="llama-3.3-70b-versatile")

list_tables = create_tool_node_with_fallback([list_tables_tool])

get_schema_tool_with_fallback = create_tool_node_with_fallback([get_schema_tool])

execute_query = create_tool_node_with_fallback([db_query_tool])

schema_prompt=ChatPromptTemplate.from_messages([("system",SCHEMA_INSTRUCTION),("placeholder","{messages}")])

category_deciding_prompt=ChatPromptTemplate.from_messages([("system",prompt),("placeholder","{messages}")])
category_deciding_llm=category_deciding_prompt|ChatGroq(model="llama-3.3-70b-versatile")

general_prompt=ChatPromptTemplate.from_messages([("system",prompt_general),("placeholder","{messages}")])
general_task_llm=general_prompt|ChatGroq(model="mixtral-8x7b-32768")



