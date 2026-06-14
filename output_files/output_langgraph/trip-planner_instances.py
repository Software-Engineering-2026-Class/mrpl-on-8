
import operator
import os
import sys
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()

# --- 1. State Definition ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# --- 2. Model Initialization ---
# We read your OPENAI_MODEL_NAME from .env but clean it up for LangChain's Google wrapper
raw_model_name = os.environ.get("OPENAI_MODEL_NAME", "gemini-1.5-flash")
clean_model_name = raw_model_name.replace("gemini/", "") if raw_model_name.startswith("gemini/") else raw_model_name

# We explicitly pass the GEMINI_API_KEY so it doesn't get confused
api_key = os.environ.get("GEMINI_API_KEY")
llm = ChatGoogleGenerativeAI(model=clean_model_name, google_api_key=api_key)

# --- 3. Node Definitions ---


def StartStep_TripPlanner_node(state: AgentState):
    '''Executes the task for GenericAgent.'''
    system_msg = SystemMessage(content="Execute task.")
    response = llm.invoke([system_msg] + state["messages"])
    return {"messages": [response]}



def Step_Extraction_node(state: AgentState):
    '''Executes the task for GenericAgent.'''
    system_msg = SystemMessage(content="Execute task.")
    response = llm.invoke([system_msg] + state["messages"])
    return {"messages": [response]}



def Step_Classify_node(state: AgentState):
    '''Executes the task for GenericAgent.'''
    system_msg = SystemMessage(content="Execute task.")
    response = llm.invoke([system_msg] + state["messages"])
    return {"messages": [response]}



def Step_CallTools_node(state: AgentState):
    '''Executes the task for GenericAgent.'''
    system_msg = SystemMessage(content="Execute task.")
    response = llm.invoke([system_msg] + state["messages"])
    return {"messages": [response]}



def EndStep_TripPlanner_node(state: AgentState):
    '''Executes the task for GenericAgent.'''
    system_msg = SystemMessage(content="Execute task.")
    response = llm.invoke([system_msg] + state["messages"])
    return {"messages": [response]}



# --- 4. Graph Orchestration ---
workflow = StateGraph(AgentState)

# Add Nodes

workflow.add_node("StartStep_TripPlanner", StartStep_TripPlanner_node)

workflow.add_node("Step_Extraction", Step_Extraction_node)

workflow.add_node("Step_Classify", Step_Classify_node)

workflow.add_node("Step_CallTools", Step_CallTools_node)

workflow.add_node("EndStep_TripPlanner", EndStep_TripPlanner_node)


# Add Entry Points (START)

workflow.add_edge(START, "StartStep_TripPlanner")


# Add Normal Edges

workflow.add_edge("StartStep_TripPlanner", "Step_Extraction")

workflow.add_edge("StartStep_TripPlanner", "Step_Classify")

workflow.add_edge("Step_Extraction", "Step_CallTools")

workflow.add_edge("Step_Extraction", "EndStep_TripPlanner")

workflow.add_edge("Step_Classify", "Step_CallTools")

workflow.add_edge("Step_Classify", "Step_Extraction")

workflow.add_edge("Step_CallTools", "EndStep_TripPlanner")


# Add Conditional Edges for cycles


# Compile the Engine
app = workflow.compile()

if __name__ == "__main__":
    print(f"LangGraph Compiled Successfully using model: {clean_model_name}.")
    print("Invoking the agent...")
    
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = input("Enter your message: ")
        
    initial_state = {"messages": [HumanMessage(content=user_input)]}
    
    try:
        result = app.invoke(initial_state)
        print("\n--- Agent Response ---")
        print(result["messages"][-1].content)
    except Exception as e:
        print(f"\nExecution Failed.\nError details: {e}")