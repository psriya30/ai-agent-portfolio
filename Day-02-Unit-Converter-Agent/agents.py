# agents.py
from smolagents import CodeAgent
from smolagents.models import LiteLLMModel
from tools import convert_units

def main():
    model = LiteLLMModel(model_id="ollama/phi3")

    agent = CodeAgent(
        tools=[convert_units],
        model=model
    )

    print("Unit Converter Agent ready ✅")
    print("Try: 'Convert 5 km to mile' OR 'Convert 100 F to C' OR type 'exit'")

    while True:
        user = input("\nYour request: ").strip()
        if user.lower() in ("exit", "quit"):
            break

        prompt = (
            "You are a unit converter agent. "
            "Extract value, from_unit, and to_unit, then use the convert_units tool. "
            f"User request: {user}"
        )
        answer = agent.run(prompt)
        print("\nAnswer:", answer)

if __name__ == "__main__":
    main()
