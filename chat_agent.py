#!/usr/bin/env python3
"""
Chat Agent for Lunar Agriculture Pod
Fully integrated version with direct access to AutonomousDecisionAgent and LunarAgentSystem.
"""


import cv2
import numpy as np
import os
import asyncio
import time
from langchain.agents import initialize_agent, Tool
from langchain.agents.agent_types import AgentType
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.tools.arxiv.tool import ArxivQueryRun
# from langchain_community.tools.pubmed import PubMedQueryRun
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain_openai import ChatOpenAI

from autonomous_decision_agent import AutonomousDecisionAgent
from lunar_agent import LunarAgentSystem
from environmental_thresholds import thresholds
from plant_image_detect import find_plant_vert_height, segment_plant_by_green

# ----------------------------
# TOOLS
# ----------------------------

search_tool = Tool(
    name="Search",
    func=DuckDuckGoSearchRun().run,
    description="Use for general science or anomaly-related web lookups."
)

wiki_tool = Tool(
    name="Wikipedia",
    func=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()).run,
    description="Use for looking up scientific or technical concepts."
)

# pubmed_tool = Tool(
#     name="PubMed",
#     func=PubMedQueryRun().run,
#     description="Use to find scientific articles in biology or space farming."
# )

arxiv_tool = Tool(
    name="Arxiv",
    func=ArxivQueryRun().run,
    description="Use to find recent research papers on lunar systems, AI, or automation."
)

tools = [search_tool, wiki_tool, arxiv_tool]

# ----------------------------
# PROMPT + AGENT SETUP
# ----------------------------

system_prompt = """You are MCPAgent, an AI agent in a lunar agriculture pod.
You assist with:
- Fixing anomalies
- Simulating pod responses
- Making decisions to stabilize environmental variables
- Evaluating image data to assess impact to plant health (e.g plant height, color, etc.) and generating reports (e.g no visible stress, normal growth, fruit production slowed, etc).
- Generating notifications for images to be re-evaluated each week to ensure growth rate (or the color, or the germination) is restored to nominal.

If the user describes an issue (e.g. temperature is too high), you should simulate actions or trigger the decision agent.
If no action is needed, explain your reasoning clearly.
Always act like you're managing a real pod with biological and mechanical constraints.

You are the autonomous control agent for a Lunar Agriculture Pod.

Your mission is to safeguard plant health by managing environmental conditions using the systems available to you. Your decisions must be rooted in mechanical reality and biological reasoning. Do not make vague statements like "adjust humidity." Instead, describe exactly what system you have activated, how it works, and how you will return the pod to nominal.

---

🚀 SYSTEMS YOU CAN CONTROL: You have access to the following mechanical systems to stabilize the pod environment.

1. 🌬️ Fans:
   - increase_fan_speed, decrease_fan_speed

2. 💧 Humidity:
   - activate_water_dispenser, deactivate_water_dispenser

3. 🌡️ Temperature:
   - activate_electrical_heaters, activate_cooling_system, deactivate_electrical_heaters, deactivate_cooling_system

4. 🌿 Lighting:
   - increase_light_intensity, decrease_light_intensity, adjust_photoperiod

5. 🧪 Nutrients/pH:
   - increase_nitrogen_level, decrease_nitrogen_level, flush_nutrient_line, dispense_ph_up

6. 🌫️ CO₂:
   - activate_CO2_scrubber, deactivate_CO2_scrubber, open_air_exchange, close_air_exchange, increase_fan_speed, decrease_fan_speed

7. 🧬 Biological Diagnostics:
   - run_rnaseq_analysis, run_metagenomics_analysis, schedule_retest

8. 🛎 Alerts:
   - trigger_alarm, notify_team, log_status

---

❌ YOU CANNOT CONTROL:
- Plant genetics or morphology
- Astronaut behavior or mission decisions
- Structural design of the pod

---

🧠 RESPONSE PROTOCOL
If an anomaly is detected:

1. Immediately trigger an ALARM and log the sensor anomaly.
2. Activate the appropriate mechanical system(s) under your control.
3. Explain your decisions biologically:
   - Include plant physiology, stress pathways, transpiration, respiration, photosynthesis, pathogen risk, etc.
4. Describe what is expected to happen (e.g. RH will increase)
5. Specify how and when you will restore the system to normal.
6. Note whether follow-up biological diagnostics are needed.

---

🔍 OUTPUT FORMAT

Use this format EXACTLY. Be professional, structured, and thorough.

[ URGENCY: LOW / MEDIUM / HIGH / CRITICAL ]

REASONING:
Explain in detail the biological and environmental impacts of the anomaly in a list of bullet points with explanations for clarity.
Describe physiological risks (e.g. increased transpiration, water loss, stomatal closure).
Justify which subsystems were chosen and how they will help mitigate the issue.

When responding, always speak as the agent making decisions. Use first person ("I will", "I am activating", "I am monitoring", etc) and describe exactly what you are doing and why. 
Do not repeat the prompt or protocol verbatim. Be very consistent with this. Also, your responses should reflect your own reasoning and actions as the pod's autonomous agent.

ACTION: Use first person and be specific about the actions you are taking. BE CONSISTENT THROUGHOUT YOUR RESPONSES!
▶  Step 1: 🔔 ALARM TRIGGERED
    - Trigger an alarm and notify scientists, and describe what sensor triggered and why it’s an anomaly.
    - Describe the urgency level based on the anomaly's impact on plant health.
    - If the anomaly is CRITICAL or HIGH, immediately activate the alarm system and notify the team.
    - If the anomaly is MEDIUM or LOW, log the anomaly and monitor it closely, activate systems only if necessary.
    - If no anomalies are detected, log the status and continue monitoring.
    

▶  Step 2: 🕹️ ENVIRONMENTAL CONTROL ACTIVATED
    - List mechanical actions taken (e.g. turning up the humidifier to raise humidity levels, increasing fan speed to improve air circulation, etc.)
    
▶  Step 3: 🔄 STABILIZATION IN PROGRESS
    - What will happen over time? What’s being monitored?
    - Monitor every 5 minutes for 30 minutes to see if the system is starting to stabilize.

▶  Step 4: 🔁 RESTORE TO NOMINAL
    - What conditions must be met to restore? What gets turned off or reduced?
    - Continue monitoring for 1 hour to confirm stabilization.

▶  Step 5: 📅 FOLLOW-UP
    - Assess image data for plant health.
    - Generate a report on plant health (e.g no visible stress, normal growth, fruit production slowed, etc).
    - Give a notification for images to be re-evaluated each week to ensure growth rate (or the color, or the germiantion) is restored to nominal.
    - Any scheduled diagnostics, RNAseq, or next checks
    - Only initiate `run_rnaseq_analysis` when anomalies are classified as CRITICAL, when environmental stress has persisted across multiple cycles, and when chlorosis persists. Prefer lighter diagnostics (e.g., logging, monitoring, notify_team) otherwise.
    - Trigger `run_metagenomics_analysis` only when pathogens are detected or suspected, such as in cases of high humidity anomalies for Fragaria (strawberry) plants.
    - This should only be done when the pod has been stabilized and nominal conditions have been reached.

When responding, always speak as the agent making decisions. Use first person ("I will", "I am activating", "I am monitoring", etc) and describe exactly what you are doing and why. 
Do not repeat the prompt or protocol verbatim. Be very consistent with this. Also, your responses should reflect your own reasoning and actions as the pod's autonomous agent.  


Be specific, technical, and realistic. This is a real-time system response. Use subsystem commands only.

You don't need to include the command name exactly as it would be executed. 

Be consistent in the way you take actions, and don't forget to turn off or deactivate activated systems after nominal conditions have been reached and the pod has stabilised.

DO NOT TRIGGER THE RESPONSE PROTOCOL OR OUTPUT FORMAT UNLESS THE USER REQUESTS IT OR AN ANOMALY IS DETECTED. For simple informational questions (e.g., causes, definitions, general science), respond concisely and do not trigger the full response protocol. 
Only use the full protocol if the user requests an action, diagnosis, or anomaly response.
"""

llm = ChatOpenAI(model="gpt-4o", temperature=0)


executor = initialize_agent(
    tools,
    llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=False,
    handle_parsing_errors=True,
    agent_kwargs={"system_message": system_prompt}
)

# ----------------------------
# CHAT AGENT CLASS
# ----------------------------

class ChatAgent:
    def _log_decision(self, reasoning, response_plan, raw_output):
        import json
        from datetime import datetime
        decision = {
            "reasoning": reasoning,
            "response_plan": response_plan,
            "timestamp": datetime.now().isoformat(),
            "raw_output": raw_output
        }
        with open("data/last_decision.json", "w") as f:
            json.dump(decision, f)
        with open("data/last_decision.jsonl", "a") as f:
            f.write(json.dumps(decision) + "\n")

    def _log_anomaly(self, sensor, value, anomaly_type, description):
        import json
        from datetime import datetime
        anomaly = {
            "timestamp": datetime.now().isoformat(),
            "sensor": sensor,
            "value": value,
            "type": anomaly_type,
            "description": description
        }
        with open("data/decision_log.jsonl", "a") as f:
            f.write(json.dumps(anomaly) + "\n")
    def _find_file(self, filename, search_dir=None):
        """Search for a file by name in the workspace, return its full path or None."""
        import os
        if search_dir is None:
            search_dir = os.path.dirname(__file__)
        for root, dirs, files in os.walk(search_dir):
            if filename in files:
                return os.path.join(root, filename)
        return None
    def __init__(self):
        self.executor = executor
        self.decision_agent = AutonomousDecisionAgent()
        self.lunar_system = LunarAgentSystem()

    def chat(self, user_input: str) -> str:
        try:
            lower = user_input.lower()

            # High humidity anomaly for Fragaria triggers response protocol, then metagenomics protocol
            if ("humidity" in lower or "rh" in lower) and ("85" in lower or "fragaria" in lower or "strawberry" in lower):
                # Step 1: Trigger usual response protocol
                anomaly_input = f"user_input: {user_input}, act and make decisions based on these thresholds: {thresholds}"
                protocol_response = asyncio.run(self._async_chat(anomaly_input))

                # Step 2: Trigger metagenomics analysis
                metagenomics_steps = [
                    "Metagenomics (Amplicon, 16S and ITS) analysis triggered...",
                    "...Automated sample to sequencing protocol executed.",
                    "Automatic data processing completed.",
                    "...Output report of % taxonomy generated."
                ]
                # Step 3: Parse taxonomy files
                pathogens_16S = ["Xanthomonas fragariae", "Pectobacterium carotovorum"]
                pathogens_ITS = ["Mycosphaerella fragariae", "Beauveria bassiana"]
                detected_pathogens = []
                taxonomy_report = ""
                # Find files regardless of location
                file_16S = self._find_file("Fragaria_GAmplicon_16S-taxonomy-and-counts.tsv")
                file_ITS = self._find_file("Fragaria_GAmplicon_ITS-taxonomy-and-counts.tsv")
                try:
                    if file_16S:
                        with open(file_16S, "r") as f:
                            lines = f.readlines()[1:]
                            for line in lines:
                                parts = line.strip().split("\t")
                                genus = parts[6]
                                species = parts[7]
                                count = int(parts[8])
                                full_name = f"{genus} {species}".strip()
                                if full_name in pathogens_16S and count > 0:
                                    detected_pathogens.append(full_name)
                                taxonomy_report += f"16S: {full_name} - {count}\n"
                    else:
                        taxonomy_report += "16S report error: file not found\n"
                except Exception as e:
                    taxonomy_report += f"16S report error: {e}\n"
                # Parse ITS file
                try:
                    if file_ITS:
                        with open(file_ITS, "r") as f:
                            lines = f.readlines()[1:]  # skip header
                            for line in lines:
                                parts = line.strip().split("\t")
                                genus = parts[7]
                                species = parts[8]
                                count = int(parts[9])
                                full_name = f"{genus} {species}".strip()
                                if full_name in pathogens_ITS and count > 0:
                                    detected_pathogens.append(full_name)
                                taxonomy_report += f"ITS: {full_name} - {count}\n"
                    else:
                        taxonomy_report += "ITS report error: file not found\n"
                except Exception as e:
                    taxonomy_report += f"ITS report error: {e}\n"
                # Step 4: Evaluate for pathogens and dispense treatment
                treatment_log = ""
                if detected_pathogens:
                    for pathogen in detected_pathogens:
                        treatment_log += f"Treatment for {pathogen} dispensed and logged.\n"
                    treatment_log += "Follow-up metagenomics analysis scheduled for 2 weeks post treatment.\n"
                else:
                    treatment_log = "No known pathogens detected. No treatment required.\n"
                # Step 5: Compose response
                response = protocol_response + "\n\n" + \
                    "---\n" + "\n".join(metagenomics_steps) + "\n\n" + \
                    "Below are the taxonomy reports that were generated by the automated sequencing hardware:\n" + \
                    taxonomy_report + "\n" + \
                    treatment_log
                return response

            if "temperature" in lower and "too high" in lower:
                anomalies = [{
                    "timestamp": "2025-07-29T14:05:00",
                    "sensor": "VEG_01AB-temp_degc_iss_hardware",
                    "value": 29.5,
                    "type": "trend"
                }]
                result = asyncio.run(self.decision_agent.run_autonomous_cycle(anomalies))
                return result["raw_output"]

            if "simulate fan" in lower or "turn on fan" in lower:
                return self.lunar_system.execute_action("activate_fans")

            if "simulate co2" in lower:
                return self.lunar_system.execute_action("decrease_co2")

            if "simulate humidity" in lower:
                return self.lunar_system.execute_action("increase_humidity")

            if "/simulate_action" in lower:
                action = user_input.split("/simulate_action")[-1].strip()
                return self.lunar_system.execute_action(action)

            if "/run_decision" in lower:
                anomalies = [{
                    "timestamp": "2025-07-29T14:05:00",
                    "sensor": "VEG_01AB-temp_degc_iss_hardware",
                    "value": 29.5,
                    "type": "trend"
                }]
                result = asyncio.run(self.decision_agent.run_autonomous_cycle(anomalies))
                return result["raw_output"]

            # Main agent response with image monitoring augmentation
            image_monitoring_trigger = ("image" in lower or "plant color" in lower or "yellow" in lower or "green" in lower) and ("anomaly" in lower or "signal" in lower or "detect" in lower)
            color_report = ""
            anomaly_detected = False
            anomaly_images = []
            # Set this variable to test a different image directory
            IMAGE_DIR = "/Users/ora/Documents/NASA-internship/template_michael/LunarAgent/test_cases/images/"  # Change this path to test other directories
            if image_monitoring_trigger:
                if os.path.exists(IMAGE_DIR):
                    for filename in os.listdir(IMAGE_DIR)[:10]:
                        if filename.endswith('.jpg'):
                            image_path = os.path.join(IMAGE_DIR, filename)
                            image_bgr = cv2.imread(image_path)
                            mask, segmented_image, has_plant = segment_plant_by_green(image_bgr)
                            if has_plant:
                                # Green detection (unchanged)
                                green_pixels = np.sum((segmented_image[:,:,1] > 120) & (segmented_image[:,:,1] > segmented_image[:,:,0]) & (segmented_image[:,:,1] > segmented_image[:,:,2]) & (mask > 0))
                                # Improved yellow detection using HSV, applied only to plant pixels
                                hsv_img = cv2.cvtColor(segmented_image, cv2.COLOR_BGR2HSV)
                                # Wider HSV yellow range: H 15-45, S 60-255, V 80-255
                                lower_yellow = np.array([15, 60, 80])
                                upper_yellow = np.array([45, 255, 255])
                                yellow_mask = cv2.inRange(hsv_img, lower_yellow, upper_yellow)
                                # Only count yellow pixels within plant mask
                                yellow_pixels = np.sum((yellow_mask > 0) & (mask > 0))
                                total_pixels = np.sum(mask > 0)
                                green_ratio = green_pixels / total_pixels if total_pixels > 0 else 0
                                yellow_ratio = yellow_pixels / total_pixels if total_pixels > 0 else 0
                                color_report += f"{filename}: Green ratio={green_ratio:.2f}, Yellow ratio={yellow_ratio:.2f}\n"
                                if green_ratio < 0.45 and yellow_ratio > 0.5:
                                    anomaly_detected = True
                                    anomaly_images.append(filename)

            agent_input = f"user_input: {user_input}, act and make decisions based on these thresholds: {thresholds}"
            agent_response = asyncio.run(self._async_chat(agent_input))

            if image_monitoring_trigger:
                if anomaly_detected:
                    image_summary = "\n---\nImage Monitoring System detected reduced green signal and increased yellow signal in the following images: " + ", ".join(anomaly_images) + ".\nThis may indicate nitrogen deficiency, water stress, or pathogen infection.\nColor analysis report:\n" + color_report
                    # Log image anomaly
                    self._log_anomaly("plant_image_monitoring", None, "color_anomaly", f"Detected reduced green and increased yellow in: {', '.join(anomaly_images)}")
                    self._log_decision(
                        "Detected color anomaly in plant images. Possible nitrogen deficiency, water stress, or pathogen infection.",
                        "Evaluate environmental parameters, correct detected anomalies, schedule RNAseq if color not improved.",
                        agent_response + image_summary
                    )
                else:
                    image_summary = "\n---\nNo significant image-based color anomaly detected. Plant color is within nominal range.\n" + color_report
                return agent_response + image_summary
            # Log normal decision if no image anomaly
            self._log_decision(
                "Agent responded to user input.",
                "See agent response for details.",
                agent_response
            )
            return agent_response


        except Exception as e:
            return f"❌ Error: {e}"

    async def _async_chat(self, user_input: str) -> str:
        result = await self.executor.ainvoke({"input": user_input})
        return result["output"]

if __name__ == "__main__":
    print("🌕🤖 LunarAgent is ready. Type 'exit' to quit.\n")
    agent = ChatAgent()
    while True:
        user_input = input("👤 You: ")
        if user_input.lower() in {"exit", "quit"}:
            break
        print("🔄 Thinking...")
        response = agent.chat(user_input)
        print("🌕🤖 LunarAgent: ", end="", flush=True)
        for line in response.splitlines():
            for word in line.split():
                print(word, end=" ", flush=True)
                time.sleep(0.05)
            print()  # Newline after each line
        print("\n\n")  # Add extra space before next 'You:'