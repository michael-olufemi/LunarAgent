#!/usr/bin/env python3
"""
Autonomous Decision Agent for Lunar Agriculture Pod
This version contains the final, definitive prompt that places reasoning before actions and mandates an action list.
"""

import logging
import os
import asyncio
from datetime import datetime
from typing import List, Dict, Any

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from environmental_thresholds import thresholds

load_dotenv()
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

AVAILABLE_ACTIONS = [
    "adjust_temperature", "adjust_humidity", "adjust_co2", "adjust_light",
    "adjust_water", "adjust_nutrients", "adjust_ph", "send_alert",
    "trigger_emergency_protocol"
]

class AutonomousDecisionAgent:
    def __init__(self, model="gpt-4o-mini", temperature=0.2):
        self.llm_enabled = bool(os.getenv("OPENAI_API_KEY"))
        if not self.llm_enabled:
            logger.warning("LLM is disabled.")
            return

        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.system_message = SystemMessage(content="You are the master controller AI for a self-driving laboratory in a Lunar Agriculture Pod. Your primary directive is to ensure optimal plant growth and survival by autonomously monitoring data streams and formulating specific, executable commands.")

    def _parse_timestamp(self, ts: Any) -> datetime:
        if isinstance(ts, datetime): return ts
        try:
            return datetime.fromisoformat(str(ts).replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return datetime.min

    def generate_decision_prompt(self, anomalies: List[Dict[str, Any]]) -> HumanMessage:
        """
        Generates the final, definitive, and re-ordered prompt for the AI.
        """
        anomaly_summary = [
            f"- {self._parse_timestamp(a.get('timestamp')).strftime('%Y-%m-%d %H:%M:%S')}: sensor '{a.get('sensor')}' ({a.get('parameter')}) reported a '{a.get('threshold_type')}' anomaly with a value of {a.get('value')}."
            for a in anomalies[:30]
        ]

        optimal_ranges_summary = [
            f"- {param}: {values.get('optimal')} (Unit: {values.get('unit', 'N/A')})".strip()
            for param, values in thresholds.items()
        ]

        # --- THIS IS THE FINAL, RE-ORDERED AND MOST EXPLICIT PROMPT ---
        prompt_content = f"""
**MISSION CRITICAL ANALYSIS & ACTION FORMULATION**

**SYSTEM:** Lunar Habitat Autonomous Control
**TIME:** {datetime.now().isoformat()}

**SITUATION:** I am the autonomous control agent for a lunar habitat. The following real-time sensor anomalies require immediate analysis and a response plan.

**ANOMALY REPORT:**
{chr(10).join(anomaly_summary)}

**OPERATIONAL PARAMETERS (OPTIMAL RANGES):**
{chr(10).join(optimal_ranges_summary)}

**DIRECTIVE:**
Analyze the anomaly report and formulate a response plan. You MUST provide a structured decision with the following three sections in this exact order. The IMMEDIATE_ACTIONS section is the most critical output and MUST NOT be empty if anomalies are present. Do not describe your actions in the reasoning; your reasoning should justify the commands you will issue in the next step.

1.  **URGENCY:** Classify the situation as LOW, MEDIUM, HIGH, or CRITICAL.

2.  **REASONING:** A concise scientific justification for the actions you are about to recommend. Explain WHY actions are necessary based on the ANOMALY REPORT and principles of plant physiology.

3.  **IMMEDIATE_ACTIONS:** A numbered list of specific, machine-readable commands based on your reasoning. This section is MANDATORY.
    -   **Strict Format:** `Action: [action_name], Target: [target_value], Unit: [unit]`
    -   **Available Action Names:** `{', '.join(AVAILABLE_ACTIONS)}`
    -   **Example 1:** `1. Action: adjust_temperature, Target: 22.5, Unit: °C`
    -   **Example 2:** `2. Action: adjust_humidity, Target: 60, Unit: %`
    -   **Example 3:** `3. Action: send_alert, Target: "Unstable temperature readings detected", Unit: "message"`
"""
        return HumanMessage(content=prompt_content)

    async def run_autonomous_cycle(self, anomalies_for_decision: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs the agent on a specific batch of anomalies using a direct LLM call."""
        if not self.llm_enabled or not anomalies_for_decision:
            return {"raw_output": "URGENCY: NONE\nIMMEDIATE_ACTIONS: None\nREASONING: LLM disabled or no anomalies to process."}

        human_message = self.generate_decision_prompt(anomalies_for_decision)
        messages = [self.system_message, human_message]
        
        try:
            response = await self.llm.ainvoke(messages)
            return {"raw_output": response.content}
        except Exception as e:
            logger.error(f"LLM direct invocation failed: {e}", exc_info=True)
            return {"raw_output": f"URGENCY: ERROR\nREASONING: An error occurred during AI processing: {e}"}