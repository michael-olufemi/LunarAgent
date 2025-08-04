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
    def execute_action(self, cmd: str):
        print(f"[EXECUTING ACTION] {cmd}")
        simulated_responses = {
            "activate_water_dispenser": "✅ Water dispenser triggered to increase water flow inside the pod.",
            "deactivate_water_dispenser": "✅ Water dispenser turned off after reaching optimal humidity.",
            "trigger_alarm": "🚨 Alarm triggered! Anomaly detected in environmental sensors.",
            "notify_team": "✅ Team has been notified about the triggered alarm.",
            "log_status": "✅ Current system status has been logged for diagnostic purposes.",
            "run_metagenomics_analysis": "✅ Follow-up metagenomics analysis scheduled.",
            "increase_fan_speed": "✅ Fan speed increased to boost air circulation.",
            "decrease_fan_speed": "✅ Fan speed decreased to reduce airflow.",
            "activate_electrical_heaters": "✅ Electrical heaters engaged to raise pod temperature.",
            "deactivate_electrical_heaters": "✅ Electrical heaters turned off after reaching optimal temperature.",
            "activate_cooling_system": "✅ Cooling system activated to reduce pod temperature.",
            "deactivate_cooling_system": "✅ Cooling system deactivated after reaching optimal temperature.",
            "open_air_exchange": "✅ Air exchange port opened to regulate CO₂ levels.",
            "close_air_exchange": "✅ Air exchange port closed after CO₂ levels returned to normal.",
            "activate_CO2_scrubber": "✅ CO₂ scrubber activated to lower carbon dioxide concentration.",
            "deactivate_CO2_scrubber": "✅ CO₂ scrubber deactivated after CO₂ levels returned to normal.",
            "adjust_photoperiod": "✅ Photoperiod adjusted to optimize light exposure.",
            "increase_light_intensity": "✅ Light intensity increased to regulate plant growth.",
            "decrease_light_intensity": "✅ Light intensity decreased for optimal plant growth.",
            "increase_nitrogen_level": "✅ Nitrogen delivery increased to support metabolic processes.",
            "decrease_nitrogen_level": "✅ Nitrogen delivery decreased to support metabolic processes.",
            "flush_nutrient_line": "✅ Nutrient line flushed to remove buildup.",
            "dispense_ph_up": "✅ pH up solution dispensed to balance acidity.",
            "run_rnaseq_analysis": "✅ RNA sequencing initiated for transcriptomic assessment.",
            "schedule_retest": "✅ Follow-up test has been scheduled."
        }
        print("    " + simulated_responses.get(cmd, "🟡 Action simulated."))

    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__) or ".", "data")
        self.anomaly_trigger_threshold = 1
        self.decision_agent = AutonomousDecisionAgent()
        self.active_controls = set()


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
        # Scan the entire LLM output for known subsystem commands
        all_output = f"{reasoning}\n{raw_output}"
        action_keywords = [
            "trigger_alarm", "notify_team", "activate_water_dispenser", "deactivate_water_dispenser",
            "log_status", "run_metagenomics_analysis", "increase_fan_speed", "decrease_fan_speed",
            "activate_electrical_heaters", "deactivate_electrical_heaters", "activate_cooling_system", "deactivate_cooling_system", "open_air_exchange", 
            "close_air_exchange", "activate_CO2_scrubber", "deactivate_CO2_scrubber",
            "adjust_photoperiod", "increase_light_intensity", "decrease_light_intensity", "increase_nitrogen_level", "decrease_nitrogen_level", "flush_nutrient_line",
            "dispense_ph_up", "run_rnaseq_analysis", "schedule_retest"
        ]    

        executed_actions = []
        for cmd in action_keywords:
            if re.search(rf"`?{re.escape(cmd)}`?", all_output, re.IGNORECASE):
                executed_actions.append(cmd)

        
        if executed_actions:
            for cmd in executed_actions:
                print(f"[SYSTEM] Executing: {cmd}")
                self.execute_action(cmd)
        else:
            print("    ❌ No executable actions were found or triggered.")
    
    
    def evaluate_stabilization(self, anomalies):
        sensors = {a['sensor']: a['value'] for a in anomalies}
        actions_to_deactivate = []

        value = next((v for k, v in sensors.items() if "rh_percent" in k), None)
        if "activate_water_dispenser" in self.active_controls and value and 45 <= value <= 70:
            actions_to_deactivate.append("deactivate_water_dispenser")
            self.active_controls.remove("activate_water_dispenser")
            
        value = next((v for k, v in sensors.items() if "rh_percent" in k), None)
        if "deactivate_water_dispenser" in self.active_controls and value and value > 70:
            actions_to_deactivate.append("activate_water_dispenser")
            self.active_controls.remove("deactivate_water_dispenser")

        value = next((v for k, v in sensors.items() if "temp_degc" in k), None)
        if "activate_electrical_heaters" in self.active_controls and value and 18 <= value <= 27:
            actions_to_deactivate.append("deactivate_electrical_heaters")
            self.active_controls.remove("activate_electrical_heaters")

        value = next((v for k, v in sensors.items() if "temp_degc" in k), None)
        if "activate_cooling_system" in self.active_controls and value and 18 <= value <= 27:
            actions_to_deactivate.append("deactivate_cooling_system")
            self.active_controls.remove("activate_cooling_system")

        value = next((v for k, v in sensors.items() if "co2_ppm" in k), None)
        if "open_air_exchange" in self.active_controls and value and 300 <= value <= 1000:
            actions_to_deactivate.append("close_air_exchange")
            self.active_controls.remove("open_air_exchange")

        value = next((v for k, v in sensors.items() if "co2_ppm" in k), None)
        if "activate_CO2_scrubber" in self.active_controls and value and 300 <= value <= 1000:
            actions_to_deactivate.append("deactivate_CO2_scrubber")
            self.active_controls.remove("activate_CO2_scrubber")
            
        value = next((v for k, v in sensors.items() if "co2_ppm" in k), None)
        if "increase_fan_speed" in self.active_controls and value and 300 <= value <= 1000:
            actions_to_deactivate.append("decerease_fan_speed")
            self.active_controls.remove("increase_fan_speed")

        for cmd in actions_to_deactivate:
            print(f"[SYSTEM] Auto-deactivating: {cmd}")
            self.execute_action(cmd)


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
                
                import os, json
                os.makedirs('data', exist_ok=True)

                # Save latest decision
                with open('data/last_decision.json', 'w') as f:
                    json.dump(decision_result, f, indent=2)

                # Append to decision log
                with open('data/decision_log.jsonl', 'a') as f:
                    f.write(json.dumps(decision_result) + '\\n')
                
                self._parse_and_print_decision(decision_result.get("raw_output", ""), anomalies_for_this_cycle)
                
                self.evaluate_stabilization(anomalies_for_this_cycle)

                
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