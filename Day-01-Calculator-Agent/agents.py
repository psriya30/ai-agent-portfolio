
# agent.py
from smolagents import CodeAgent
from smolagents.models import LiteLLMModel
from tools import calculate



def main():
    # Uses local Ollama model
    model = LiteLLMModel(model_id="ollama/phi3")

    agent = CodeAgent(
        tools=[calculate],
        model=model
    )

    print("Calculator Agent ready. Try: 25 * 48  OR  (10+2)**3")
    while True:
        expr = input("\nEnter expression (or 'exit'): ").strip()
        if expr.lower() in ("exit", "quit"):
            break
        answer = agent.run(f"Calculate this exactly: {expr}. Use the calculate tool.")
        print("\nAnswer:", answer)

if __name__ == "__main__":
    main()


