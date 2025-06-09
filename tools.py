import json
from typing import Optional
from langchain_core.tools import tool

# === Read Anomaly Logs (with optional sensor filtering) ===
def get_recent_anomalies(n: int = 5, sensor: Optional[str] = None) -> str:
    try:
        with open("anomaly_log.jsonl", "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        entries = [json.loads(line) for line in lines]
        if sensor:
            entries = [e for e in entries if e.get("sensor") == sensor]

        # Sort by timestamp descending
        entries.sort(key=lambda x: x["timestamp"], reverse=True)
        latest = entries[:n]

        if not latest:
            return f"🔍 No anomalies found for sensor '{sensor}'." if sensor else "🔍 No anomalies found."

        return "\n".join([
            f"{e['sensor']} | {e['timestamp']} — {e['value']} (z={e['z_score']:.2f})"
            for e in latest
        ])

    except Exception as e:
        return f"⚠️ Could not load logs: {e}"

# === LangChain Tools ===

@tool
def anomaly_log_tool(n: int = 5, sensor: Optional[str] = None) -> str:
    """
    Get the most recent N anomalies. Optionally filter by sensor (e.g., 'co2-1', 'temp-1').
    """
    return get_recent_anomalies(n=n, sensor=sensor)

@tool
def wiki_tool(query: str) -> str:
    """Search Wikipedia and return a summary."""
    from langchain_community.tools import WikipediaQueryRun
    return WikipediaQueryRun().run(query)

@tool
def search_tool(query: str) -> str:
    """Search DuckDuckGo and return search result snippets."""
    from langchain_community.tools import DuckDuckGoSearchResults
    return DuckDuckGoSearchResults().run(query)

@tool
def pubmed_tool(query: str) -> str:
    """Search PubMed for biomedical literature on CO₂, temperature, RH, or plant stress."""
    from langchain_community.tools import PubmedQueryRun
    return PubmedQueryRun().run(query)

@tool
def arxiv_tool(query: str) -> str:
    """Search arXiv for scientific literature on environmental monitoring and plant AI applications."""
    from langchain_community.tools import ArxivQueryRun
    return ArxivQueryRun().run(query)
