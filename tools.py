import json
from langchain_core.tools import tool

# === Tool: Read Anomaly Logs ===
def get_recent_anomalies(n=5):
    try:
        with open("anomaly_log.jsonl", "r") as f:
            lines = f.readlines()
        entries = [json.loads(line) for line in lines[-n:]]
        return "\n".join([f"{e['timestamp']} | CO₂: {e['co2_ppm']} ppm | z={e['z_score']:.2f}" for e in entries])
    except Exception as e:
        return f"⚠️ Could not load logs: {e}"

@tool
def anomaly_log_tool(n: int = 5) -> str:
    """Get the most recent N anomalies detected in the MCPApp logs."""
    return get_recent_anomalies(n)

@tool
def wiki_tool(query: str) -> str:
    """Search Wikipedia and return a summary."""
    from langchain_community.tools import WikipediaQueryRun
    return WikipediaQueryRun().run(query)

@tool
def search_tool(query: str) -> str:
    """Search DuckDuckGo and return results."""
    from langchain_community.tools import DuckDuckGoSearchResults
    return DuckDuckGoSearchResults().run(query)
