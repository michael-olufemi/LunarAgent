from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from tools import anomaly_log_tool, search_tool, wiki_tool, arxiv_tool, pubmed_tool

# === Load API key ===
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise EnvironmentError("❌ OPENAI_API_KEY not found. Please add it to your .env file.")

# === Set up LLM ===
llm = ChatOpenAI(model="gpt-4", temperature=0)

# === Prompt template ===
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are MCPAgent, an AI assistant for monitoring a lunar agriculture pod.
You can detect anomalies, explain sensor behavior, and look up scientific literature to justify responses.
Use available tools when needed. Do not guess. Use PubMed or arXiv to answer scientific or biological questions."""
    ),
    ("user", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# === Register tools ===
tools = [anomaly_log_tool, search_tool, wiki_tool, pubmed_tool, arxiv_tool]

# === Create agent ===
agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# === Chat loop ===
if __name__ == "__main__":
    print("🤖 MCPAgent is ready. Type 'exit' to quit.\n")
    while True:
        user_input = input("👩‍🚀 You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 MCPAgent exiting.")
            break
        try:
            response = executor.invoke({"input": user_input})
            print(f"🤖 MCPAgent: {response['output']}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
