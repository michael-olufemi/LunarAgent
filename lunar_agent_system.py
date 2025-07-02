#!/usr/bin/env python3
"""
Integrated Lunar Agriculture Pod Agent System (Immediate Decision Mode)
This version contains the final, definitive logic for parsing and displaying decisions correctly.
"""
import asyncio
import logging
import os
import re
from datetime import datetime

from dotenv import load_dotenv

from autonomous_decision_agent import AutonomousDecisionAgent
from detector import ANOMALY_LOG
from streamer import stream_all_events_to_classifier

load_dotenv()
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class LunarAgentSystem:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__) or ".", "data")
        self.anomaly_trigger_threshold = 1
        self.decision_agent = AutonomousDecisionAgent()

    def _parse_and_print_decision(self, raw_output: str, anomalies: list):
        """
        Parses the raw text output from the LLM and prints a clean, formatted decision.
        
        """
        print("\n  ANOMALIES IN THIS CYCLE:")
        for anomaly in anomalies[:5]: # Print up to 5 for brevity
             ts_obj = anomaly.get('timestamp')
             ts = ts_obj.strftime('%H:%M:%S') if isinstance(ts_obj, datetime) else "N/A"
             sensor = anomaly.get('sensor')
             value = anomaly.get('value')
             atype = anomaly.get('threshold_type')
             print(f"    - [{ts}] {sensor}: {value} (Type: {atype})")
        if len(anomalies) > 5:
            print(f"    - ... and {len(anomalies) - 5} more.")

        # --- THIS IS THE FINAL, DEFINITIVE PARSING LOGIC ---
        urgency, reasoning, actions = "UNKNOWN", "No reasoning provided.", []

        # Use more specific, non-greedy regex to find each section independently.
        # This handles the reordered output correctly.
        urgency_match = re.search(r"URGENCY:\s*(.*?)\n", raw_output, re.IGNORECASE)
        # This regex stops at the "IMMEDIATE_ACTIONS" header, preventing the duplication.
        reasoning_match = re.search(r"REASONING:\s*(.*?)(?=\n\d*\.?\s*IMMEDIATE_ACTIONS:|\Z)", raw_output, re.IGNORECASE | re.DOTALL)
        # This regex specifically finds the "IMMEDIATE_ACTIONS" section, even if it's numbered.
        actions_match = re.search(r"IMMEDIATE_ACTIONS:\s*\n(.*?)$", raw_output, re.IGNORECASE | re.DOTALL)

        if urgency_match:
            urgency = urgency_match.group(1).strip().replace('*', '')
        
        if reasoning_match:
            reasoning = reasoning_match.group(1).strip().replace('*', '')
        
        if actions_match:
            actions_text = actions_match.group(1).strip()
            # This ensures we only capture lines that are formatted as actions.
            actions = [line.strip() for line in actions_text.split('\n') if "Action:" in line]
        
        # --- Print the cleaned and formatted output in the correct order ---
        print(f"\n[ URGENCY: {urgency} ]")
        
        print("\n  REASONING:")
        print(f"    {reasoning}")

        print("\n  IMMEDIATE ACTIONS:")
        # The 'else' statement has been removed as requested.
        # Now, it will only print the actions it finds.
        for action in actions:
                clean_action = re.sub(r"^\d\.\s*", "", action)
                print(f"    - {clean_action}")
        

    async def _check_decision_trigger_loop(self):
        """Continuously checks for anomalies and triggers the decision agent."""
        await asyncio.sleep(10)
        print("--- Autonomous Decision Agent is now active (Immediate Decision Mode). ---")

        while True:
            await asyncio.sleep(0.1)
            
            if len(ANOMALY_LOG) >= self.anomaly_trigger_threshold:
                anomalies_for_this_cycle = list(ANOMALY_LOG)
                ANOMALY_LOG.clear()
                
                print("\n" + "="*80)
                print(f"DECISION CYCLE TRIGGERED ({len(anomalies_for_this_cycle)} anomalies) - {datetime.now().isoformat()}")
                print("="*80)
                
                decision_result = await self.decision_agent.run_autonomous_cycle(anomalies_for_this_cycle)
                
                self._parse_and_print_decision(decision_result.get("raw_output", ""), anomalies_for_this_cycle)
                
                print("\n" + "="*80)

    async def run(self):
        """Main asynchronous run method."""
        streaming_task = asyncio.create_task(stream_all_events_to_classifier(self.data_dir))
        decision_loop_task = asyncio.create_task(self._check_decision_trigger_loop())
        try:
            await asyncio.gather(streaming_task, decision_loop_task)
        except asyncio.CancelledError:
            logger.info("System tasks cancelled.")

def main():
    try:
        system = LunarAgentSystem()
        asyncio.run(system.run())
    except KeyboardInterrupt:
        print("\n⏹️ System stopped by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        logger.error("Main system loop error", exc_info=True)

if __name__ == "__main__":
    main()