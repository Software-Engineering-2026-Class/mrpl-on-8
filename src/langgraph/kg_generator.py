import os

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