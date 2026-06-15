import os
import sys
import rdflib
from jinja2 import Environment, DictLoader

class AgentOGenerator:
    """
    Generates executable LangGraph Python scripts from AgentO Knowledge Graphs.

    Pipeline: .ttl (Turtle) → SPARQL extraction → topology dict → Jinja2 template → .py

    The generator handles three graph topologies:
      - Linear chains   (A → B → C → END)
      - Branching graphs (A → B, A → C)
      - Cyclic graphs    (A → B → A) — uses DFS to detect back-edges and
                          injects conditional routing to prevent infinite loops.
    """
    def __init__(self, ttl_path: str):
        self.graph = rdflib.Graph()
        self.graph.parse(ttl_path, format="turtle")
        self.ns = "http://www.w3id.org/agentic-ai/onto#"
        
    def extract_topology(self) -> dict:
        """Queries the KG to extract nodes, edges, and nested patterns."""
        
        query = f"""
        PREFIX agento: <{self.ns}>
        PREFIX dct: <http://purl.org/dc/terms/>
        
        SELECT ?step ?title ?nextStep ?subPattern ?agentTitle ?prompt
        WHERE {{
            ?pattern agento:hasWorkflowStep ?step .
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
            
            if step_id not in nodes:
                nodes[step_id] = {
                    "id": step_id,
                    "title": title,
                    "agent": str(row.agentTitle) if row.agentTitle else "GenericAgent",
                    "prompt": repr(str(row.prompt).strip()) if row.prompt else repr("Execute task."),
                    "is_nested": False
                }
            
            if row.subPattern:
                nodes[step_id]["is_nested"] = True
                nested_graphs[step_id] = str(row.subPattern).split("#")[-1]
                
            if row.nextStep:
                next_id = str(row.nextStep).split("#")[-1]
                edges.append((step_id, next_id))
                
        # Post-process edges: if a destination is not in nodes, it's an end step
        processed_edges = []
        for src, dst in set(edges):
            if dst not in nodes:
                processed_edges.append((src, "END"))
            else:
                processed_edges.append((src, dst))

        # Calculate Entry Points
        all_destinations = {edge[1] for edge in processed_edges}
        entry_points = [node_id for node_id in nodes if node_id not in all_destinations]
        if not entry_points and nodes:
            entry_points = [list(nodes.keys())[0]]
            
        # Detect cycles (back-edges)
        from collections import defaultdict
        adj = defaultdict(list)
        for u, v in edges:
            adj[u].append(v)
            
        visited = set()
        recursion_stack = set()
        back_edges = set()
        
        def dfs(node):
            visited.add(node)
            recursion_stack.add(node)
            for neighbor in adj[node]:
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in recursion_stack:
                    back_edges.add((node, neighbor))
            recursion_stack.remove(node)
            
        for ep in entry_points:
            dfs(ep)
            
        normal_edges = [e for e in edges if e not in back_edges]
        conditional_edges = [e for e in edges if e in back_edges]
                
        return {
            "nodes": list(nodes.values()),
            "edges": processed_edges,
            "normal_edges": normal_edges,
            "conditional_edges": conditional_edges,
            "nested": nested_graphs,
            "entry_points": entry_points
        }

    def generate_code(self, topology: dict) -> str:
        """Feeds the topology into the LangGraph Jinja template."""
        
        template_string = """
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
{% for node in nodes %}
{% if not node.is_nested %}
def {{ node.id }}_node(state: AgentState):
    '''Executes the task for {{ node.agent }}.'''
    system_msg = SystemMessage(content={{ node.prompt }})
    response = llm.invoke([system_msg] + state["messages"])
    return {"messages": [response]}
{% else %}
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

# Add Entry Points (START)
{% for ep in entry_points %}
workflow.add_edge(START, "{{ ep }}")
{% endfor %}

# Add Edges
{% for edge in edges %}
{% if edge[1] == 'END' %}
workflow.add_edge("{{ edge[0] }}", END)
{% else %}
# Add Normal Edges
{% for edge in normal_edges %}
workflow.add_edge("{{ edge[0] }}", "{{ edge[1] }}")
{% endif %}
{% endfor %}

# Add Conditional Edges for cycles
{% for edge in conditional_edges %}
def router_{{ edge[0] }}_{{ edge[1] }}(state: AgentState):
    if len(state["messages"]) > 10:
        return "end"
    return "continue"

workflow.add_conditional_edges(
    "{{ edge[0] }}",
    router_{{ edge[0] }}_{{ edge[1] }},
    {
        "continue": "{{ edge[1] }}",
        "end": END
    }
)
{% endfor %}

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
        print("\\n--- Agent Response ---")
        print(result["messages"][-1].content)
    except Exception as e:
        print(f"\\nExecution Failed.\\nError details: {e}")
"""
        env = Environment(loader=DictLoader({'langgraph_main': template_string}))
        template = env.get_template('langgraph_main')
        return template.render(
            nodes=topology["nodes"], 
            normal_edges=topology["normal_edges"],
            conditional_edges=topology["conditional_edges"],
            nested=topology["nested"],
            entry_points=topology["entry_points"]
        )

# Execution
if __name__ == "__main__":
    if len(sys.argv) > 2:
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
    else:
        input_dir = input("Enter input directory path (e.g. generated_kg/LangGraph/): ") or "generated_kg/LangGraph/"
        output_dir = input("Enter output directory path (e.g. output_files/output_langgraph/): ") or "output_files/output_langgraph/"
    
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith(".ttl"):
            input_file = os.path.join(input_dir, filename)
            
            generator = AgentOGenerator(input_file)
            topology_data = generator.extract_topology()
            executable_python_code = generator.generate_code(topology_data)
            
            output_filename = filename.replace(".ttl", ".py")
            output_path = os.path.join(output_dir, output_filename)
            with open(output_path, "w") as f:
                f.write(executable_python_code)
                
            print(f"Success! LangGraph project generated at: {output_path}")
