# MCPAgent: AI Anomaly Detection + Chat Agent

This project combines a real-time anomaly detection engine for CO₂ readings with a LangChain-powered AI agent capable of answering questions and querying logs via chat.

## Features
- Realtime anomaly detection from CSV stream
- Decision engine for managing alerts
- LangChain + OpenAI GPT-4 powered chat interface
- Tools for Wikipedia, DuckDuckGo search, and internal anomaly log access

## Usage

```bash
# Terminal 1
python mcp_streamer.py

# Terminal 2
python chat_agent.py
See requirements.txt

Place your OpenAI key in .env like:
OPENAI_API_KEY=sk-...
