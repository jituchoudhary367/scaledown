import os
import sys

from dotenv import load_dotenv

load_dotenv()

# Ensure scaledown and local agents are in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from agents import create_research_graph

def main():
    print("Initializing Research Agent...")
    try:
        graph = create_research_graph()
    except Exception as e:
        print(f"Failed to create graph: {e}")
        return

    # Check for API key (sanity check before running)
    if not os.getenv("OPENROUTER_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("WARNING: No API key found. Please set OPENROUTER_API_KEY or OPENAI_API_KEY in .env")
        print("The agent will likely fail when it tries to call the LLM.")
    
    if not os.getenv("SCALEDOWN_API_KEY"):
        print("WARNING: SCALEDOWN_API_KEY not found. Context compression via ScaleDown API will fall back to raw text.")

    query = "What are the latest advancements in Solid State Batteries as of 2024-2025?"
    print(f"\nRunning query: {query}\n")
    
    inputs = {"task": query, "iteration": 0}
    
    try:
        for output in graph.stream(inputs):
            for key, value in output.items():
                print(f"Finished node: {key}")
                if key == "writer":
                    print("\n--- FINAL REPORT ---\n")
                    print(value.get("report", "No report generated."))
                elif key == "critic":
                    conf = value.get("confidence", 0.0)
                    print(f"Confidence: {conf:.2f}")
    except Exception as e:
        print(f"Error during execution: {e}")

if __name__ == "__main__":
    main()
