import os
import rdflib
from jinja2 import Environment, DictLoader

class AgentOGenerator:
    def __init__(self, ttl_path: str):
        self.graph = rdflib.Graph()
        self.graph.parse(ttl_path, format="turtle")
        
        # Define namespace for cleaner queries
        self.ns = "http://www.w3id.org/agentic-ai/onto#"
        
    def extract_topology(self) -> dict:
        """
        Queries the KG to extract nodes, edges, and nested patterns.
        Identifies Sequential, Parallel, and Nested structures.
        """
        query = f"""
        PREFIX agento: <{self.ns}>
        PREFIX dct: <http://purl.org/dc/terms/>
        
        SELECT ?step ?title ?nextStep ?subPattern ?agentTitle ?prompt
        WHERE {{
            ?step a agento:WorkflowStep .
            OPTIONAL {{ ?step dct:title ?title . }}
            OPTIONAL {{ ?step agento:nextStep ?nextStep . }}
            OPTIONAL {{ ?step agento:hasSubPattern ?subPattern . }}
            OPTIONAL {{ 
                ?step agento:hasAssociatedTask ?task .
                ?task agento:performedByAgent ?agent .
                ?agent dct:title ?agentTitle .
                ?agent agento:agentPrompt ?promptNode .
                ?promptNode agento:promptInstruction ?prompt .
            }}
        }}
        """
        
        results = self.graph.query(query)
        nodes = {}
        edges = []
        nested_graphs = {}
        
        for row in results:
            step_id = str(row.step).split("#")[-1]
            title = str(row.title) if row.title else step_id
            
            # Register Node
            if step_id not in nodes:
                nodes[step_id] = {
                    "id": step_id,
                    "title": title,
                    "agent": str(row.agentTitle) if row.agentTitle else "GenericAgent",
                    "prompt": str(row.prompt) if row.prompt else "Execute task.",
                    "is_nested": False
                }
            
            # Detect Nested (Subgraph) Pattern
            if row.subPattern:
                nodes[step_id]["is_nested"] = True
                nested_graphs[step_id] = str(row.subPattern).split("#")[-1]
                
            # Detect Edges
            if row.nextStep:
                next_id = str(row.nextStep).split("#")[-1]
                edges.append((step_id, next_id))
                
        return {
            "nodes": list(nodes.values()),
            "edges": list(set(edges)),
            "nested": nested_graphs
        }

    def generate_code(self, topology: dict) -> str:
        """Feeds the topology into the LangGraph Jinja template."""
        
        # Jinja template for LangGraph output (Using OpenAI Wrapper for Gemini via .env)
        template_string = """
import operator
import os
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

# --- 1. State Definition ---
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# --- 2. Model Initialization (Option 1 Audit approach) ---
model_name = os.environ.get("OPENAI_MODEL_NAME", "gemini-3.1-flash-lite")
llm = ChatOpenAI(model=model_name)

# --- 3. Node Definitions ---
{% for node in nodes %}
{% if not node.is_nested %}
def {{ node.id }}_node(state: AgentState):
    '''Executes the task for {{ node.agent }}.'''
    system_msg = SystemMessage(content="{{ node.prompt }}")
    
    # LangChain's ChatOpenAI wrapper expects messages, not raw strings
    response = llm.invoke([system_msg] + state["messages"])
    return {"messages": [response]}
{% else %}
# Subgraph (Nested Pattern) for {{ node.id }} would be compiled here
def {{ node.id }}_node(state: AgentState):
    return {"messages": [SystemMessage(content="Nested execution complete.")]}
{% endif %}
{% endfor %}

# --- 4. Graph Orchestration ---
workflow = StateGraph(AgentState)

# Add Nodes
{% for node in nodes %}
workflow.add_node("{{ node.id }}", {{ node.id }}_node)
{% endfor %}

# Add Edges
{% for edge in edges %}
workflow.add_edge("{{ edge[0] }}", "{{ edge[1] }}")
{% endfor %}

# Compile the Engine
app = workflow.compile()

if __name__ == "__main__":
    print(f"LangGraph Compiled Successfully using model: {model_name}.")
    
    print("Invoking the agent...")
    initial_state = {"messages": [HumanMessage(content="Hello! Can you help me plan a trip?")]}
    
    try:
        result = app.invoke(initial_state)
        print("\\n--- Agent Response ---")
        print(result["messages"][-1].content)
    except Exception as e:
        print(f"\\nExecution Failed. Ensure your .env variables (OPENAI_MODEL_NAME and API keys) are correct.\\nError details: {e}")
"""
        
        env = Environment(loader=DictLoader({'langgraph_main': template_string}))
        template = env.get_template('langgraph_main')
        return template.render(
            nodes=topology["nodes"], 
            edges=topology["edges"],
            nested=topology["nested"]
        )

# Execution
if __name__ == "__main__":
    # Define absolute or relative paths based on your repo structure
    input_file = "../../generated_kg/LangGraph/chat-agent_instances.ttl"
    output_dir = "../../output_files/output_langgraph/"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Run the generator
    generator = AgentOGenerator(input_file)
    topology_data = generator.extract_topology()
    executable_python_code = generator.generate_code(topology_data)
    
    # Save the output
    output_path = os.path.join(output_dir, "generated_langgraph_app.py")
    with open(output_path, "w") as f:
        f.write(executable_python_code)
        
    print(f"Success! LangGraph project generated at: {output_path}")