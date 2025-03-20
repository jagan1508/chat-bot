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

set_variables()

def load_db(username : str, password: str, host: str, port : str ,database: str):
    db = SQLDatabase.from_uri(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}",sample_rows_in_table_info = 3)
    #print(db.dialect)
    #print(db.get_usable_table_names())
    return db

db=load_db(username="root", password="jagan2911", host="mysqlserver",port="3306",database="employeez")
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
    model=ChatGroq(model="qwen-2.5-32b")
    relevant_tables=model.invoke(prompt)
    #print("relevant tables ",relevant_tables.content)
    relevant_tables=parse(relevant_tables.content)
    
    if not relevant_tables:
        return {"error_message": INVALID_QUESTION_ERROR,"tables_info":"No relevant tables"}
    tables_info=db.get_table_info(relevant_tables)
    #print(tables_info)
    
    return {"tables_info": tables_info, 'attempts':0 , 'answer':'','error_message':'','reasoning':'','answer':''}

def generate_query(state: OverallState) -> OverallState:
    question= state["question"]
    tables_info=state["tables_info"]
    queries=state.get("queries")
    attempts=state.get("attempts")
    
    #print("past queries",queries)
    #print("question",question)
    if queries:  
        if queries[-1].is_valid ==True:
            instructions= (GENERATE_QUERY_INSTRUCTIONS.format(info=tables_info, queries=queries))
        else:
            instructions= (FIX_QUERY_INSTRUCTIONS.format(info=tables_info, error_info=queries[-1].error_info))
    else:
        instructions= (GENERATE_QUERY_INSTRUCTIONS.format(info=tables_info,queries=queries))
    
    
    generator_prompt=[SystemMessage(content=instructions)]+[HumanMessage(content=question)]

    generator_model=ChatGroq(model="deepseek-r1-distill-llama-70b").with_structured_output(GenQueryResponse)
    generator_response=generator_model.invoke(generator_prompt)
    #print("generated statement ",generator_response.statement)
    #print("generated reasoning ",generator_response.reasoning)
    
    ##checker
    checker_prompt=([SystemMessage(content=QUERY_CHECK_INSTRUCTION)]+
                    [AIMessage(content=f"SQLite query: {generator_response.statement}\n Reasoning:{generator_response.reasoning}")]
                    )
    checker_model=ChatGroq(model="llama-3.3-70b-specdec").with_structured_output(GenQueryResponse)
    checker_response= checker_model.invoke(checker_prompt)
    
    corrected=generator_response.statement != checker_response.statement
    #print("Query correction status ",corrected)
    if corrected:
        final_reasoning= f"First: {generator_response.reasoning}\nCorrection: {checker_response.reasoning}"
    else:
        final_reasoning=generator_response.reasoning
    
    #print(checker_response.statement,final_reasoning)
    query=Query(statement=checker_response.statement, reasoning=final_reasoning)
    
    return {"queries":[query],"attempts":state["attempts"]+1}

def execute_query(state: OverallState)-> OverallState:
    attempts=state["attempts"]
    max_attempts=state["max_attempts"]
    query=state["queries"][-1]
    #print("attempts",attempts)
    #print("max_attempts",max_attempts)
    if attempts >max_attempts:
        return {"error_message": REACH_OUT_MAX_ATTEMPTS_ERROR}
    #print("In executing this query :", query)
    try:
        query_result=db.run(query.statement)
        #print("this is the result on running this query ", query_result)
        if query_result:
            query.result=query_result
        else:
            query.result="No result found"
    except Exception as e:
        print("Exception")
        #print(e)
        query.result="ERROR:"+str(e)
        query.is_valid=False 
    return {"attempts": state["attempts"]}

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
    print("helleooeoe")
    message_history=state["general_message"]
    pack=GeneralMessage()
    pack.human=statement
    chat_instruction=NORMAL_INSTRUCTION.format(history=message_history)
    general_prompt=ChatPromptTemplate.from_messages([("system",chat_instruction),("placeholder","{messages}")])
    general_task_llm=general_prompt|ChatGroq(model="mixtral-8x7b-32768")
    response=general_task_llm.invoke({"messages":[statement]})
    #print("response from general chat: ",response.human)
    #print("response from general chat: ",response.llm)
    pack.llm=response.content
    
    
    return {"answer":response.content,"general_message":[pack]}

def is_related(state):
    statement=state['question']
    tables_info=state["tables_info"]
    #print(tables_info)
    #print(statement)
    category_deciding_instruction=SystemMessage(content=CATEGORY_DECIDING_PROMPT.format(statement=statement,tables_info=tables_info))
    category_deciding_llm=ChatGroq(model="mixtral-8x7b-32768")
    response=category_deciding_llm.invoke([category_deciding_instruction])
    #print(response.content)
    if response.content.lower()=="sql" or "sql" in response.content.lower():
        return True
    else:
        #print(statement)
        return False

def check_question(state: OverallState) -> Literal["generate_query","generate_answer","general_chat"]:
    if is_related(state):        
        if state.get("error_message") == INVALID_QUESTION_ERROR :
            return "general_chat"
        return "generate_query"
    else:
        return "general_chat"

def router(state:OverallState) -> Literal["generate_query","generate_answer"]:
    query=state["queries"][-1]
    #print("\nresult of query",query.result)
    if query.result.startswith("ERROR"):
        return "generate_query"
    else:
        return "generate_answer"
    


    
