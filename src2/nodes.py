from langchain_community.utilities import SQLDatabase
from  set_api_keys import *
from prompts import *
from states import *
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.errors import NodeInterrupt
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.prompts import ChatPromptTemplate
from typing import Literal




def set_variables():
    set_env("GROQ_API_KEY")
    set_env("LANGCHAIN_API_KEY")
    os.environ["LANGCHAIN_TRACING_V2"]="true"
    os.environ["LANGCHAIN_PROJECT"]="sql-llm-agent-tracker"

def load_db(username : str, password: str, host: str, database: str):
    db = SQLDatabase.from_uri(f"mysql+pymysql://{username}:{password}@{host}/{database}",sample_rows_in_table_info = 3)
    #print(db.dialect)
    #print(db.get_usable_table_names())
    return db

db=load_db(username="root", password="jagan2911", host="localhost",database="employeez")
import ast
def parse(tables):
    result=ast.literal_eval(tables)
    return result
    
    

def select_relevant_schemas(state: InputState) -> OverallState:
    max_attempts=state.get('max_attempts',0)
    if state['max_attempts']>0:
        state['max_attempts']=max_attempts
    else:
        state['max_attempts']=MAX_ATTEMPTS_DEFAULT
    table_names=db.get_usable_table_names()
    question= state['question']
    toolkit= SQLDatabaseToolkit(db=db, llm=ChatGroq(model="mixtral-8x7b-32768"))
    tools= toolkit.get_tools()
    get_schema_tool=next(tool for tool in tools if tool.name=="sql_db_schema")
    tables_with_schema=dict()
    for i in table_names:
        #print(get_schema_tool.invoke(i))
        tables_with_schema[i]=get_schema_tool.invoke(i)
    #print("table_names", table_names)
    
    instruction=SystemMessage(content=SELECT_RELEVANT_TABLES_INSTRUCTION.format(table_names=table_names))
    prompt=[instruction]+[HumanMessage(content=question)]
    #print(prompt)
    model=ChatGroq(model="llama-3.3-70b-versatile")
    relevant_tables=model.invoke(prompt)
    #print("relevant tables ",relevant_tables.content)
    relevant_tables=parse(relevant_tables.content)
    
    if not relevant_tables:
        return {"error_message": INVALID_QUESTION_ERROR}
    tables_info=db.get_table_info(relevant_tables)
    #print(tables_info)
    
    return {"tables_info": tables_info, 'attempts':1 , **state}

def generate_query(state: OverallState) -> OverallState:
    question= state["question"]
    tables_info=state["tables_info"]
    queries=state.get("queries")
    
    if not queries:
        instructions= (GENERATE_QUERY_INSTRUCTIONS.format(info=tables_info))
    else:
        instructions= (FIX_QUERY_INSTRUCTIONS.format(info=tables_info, error_info=queries[-1].error_info))
    
    generator_prompt=[SystemMessage(content=instructions)]+[HumanMessage(content=question)]

    generator_model=ChatGroq(model="llama-3.3-70b-versatile").with_structured_output(GenQueryResponse)
    generator_response=generator_model.invoke(generator_prompt)
    #print("generated statement ",generator_response.statement)
    #print("generated reasoning ",generator_response.reasoning)
    
    ##checker
    checker_prompt=([SystemMessage(content=QUERY_CHECK_INSTRUCTION)]+
                    [AIMessage(content=f"SQLite query: {generator_response.statement}\n Reasoning:{generator_response.reasoning}")]
                    )
    checker_model=ChatGroq(model="llama-3.3-70b-versatile").with_structured_output(GenQueryResponse)
    checker_response= checker_model.invoke(checker_prompt)
    
    corrected=generator_response.statement != checker_response.statement
    #print("Query correction status ",corrected)
    if corrected:
        final_reasoning= f"First: {generator_response.reasoning}\nCorrection: {checker_response.reasoning}"
    else:
        final_reasoning=generator_response.reasoning
    
    #print(checker_response.statement,final_reasoning)
    query=Query(statement=checker_response.statement, reasoning=final_reasoning)
    
    return {"queries":[query]}

def execute_query(state: OverallState)-> OverallState:
    attempts=state["attempts"]
    max_attempts=state["max_attempts"]
    query=state["queries"][-1]
    #print("In executing this query :", query)
    try:
        query_result=db.run(query.statement)
        #print("this is the result on running this query ", query_result)
        query.result=query_result
    except Exception as e:
        query.result=str(e)
        query.is_valid=False
        if attempts >=max_attempts:
            return {"error_message": REACH_OUT_MAX_ATTEMPTS_ERROR}
    return {"attempts": 1}

def generate_answer(state: OverallState) -> OutputState:
    if error_message := state.get("error_message"):
        return {"error_message": error_message}
    query=state["queries"][-1]
    generate_answer_ins=GENERATE_ANSWER_INSTRUCTION.format(query_info=query.info)
    #print("query on info: ",query.info)
    prompt=(
        [SystemMessage(content=generate_answer_ins)] +
        [HumanMessage(content=state["question"])]
    )
    
    response= ChatGroq(model="qwen-2.5-32b").invoke(prompt)
    
    return {"answer":response.content}

def general_chat(state: InputState) -> OutputState:
    statement=state['question']
    general_prompt=ChatPromptTemplate.from_messages([("system",NORMAL_INSTRUCTION),("placeholder","{messages}")])
    general_task_llm=general_prompt|ChatGroq(model="mixtral-8x7b-32768")
    response=general_task_llm.invoke({"messages":[statement]})
    #print("response from general chat: ",response.content)
    return {"answer":response.content}


def check_question(state: OverallState) -> Literal["generate_query","generate_answer"]:
    if state.get("error_message") == INVALID_QUESTION_ERROR:
        return "generate_answer"
    return "generate_query"

def router(state:OverallState) -> Literal["generate_query","generate_answer"]:
    query=state["queries"][-1]
    #print("\nresult of query",query.result)
    if query.result:
        return "generate_answer"
    else:
        return "generate_query"
    
def categorise(state: InputState) -> Literal["select_relevant_schemas","general_chat"]:
    statement=state['question']
    #print(statement)
    category_deciding_instruction=SystemMessage(content=CATEGORY_DECIDING_PROMPT.format(statement=statement))
    category_deciding_llm=ChatGroq(model="mixtral-8x7b-32768")
    response=category_deciding_llm.invoke([category_deciding_instruction])
    #print(response.content)
    if response.content=="sql":
        return "select_relevant_schemas"
    else:
        #print(statement)
        return "general_chat"


    
