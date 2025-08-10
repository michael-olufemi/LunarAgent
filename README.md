# AI Agent for a Simulated Lunar Agriculture Pod 

This project is an autonomous AI agent for managing a lunar agriculture pod. It detects environmental and image-based anomalies, makes realistic decisions, runs metagenomics workflows, and provides actionable reports. The agent can screen for plant pathogens and query research articles for detected pathogens.

## Project Directory Structure

```
LunarAgent/
├── chat_agent.py
├── lunar_agent_system.py
├── plant_image_detect.py
├── schemas.py
├── streamlit_app.py
├── tools.py
├── streamer.py
├── detector.py
├── classifier.py
├── all_sensors.py
├── all_sensors.txt
├── autonomous_decision_agent.py
├── requirements.txt
├── edeniss2020_updated.csv
├── environmental_thresholds.py
├── data/
│   ├── edeniss2020/
│   ├── exolab_images/
│   ├── APEX/
│   ├── VEG/
│   ├── last_decision.json
│   ├── decision_log.jsonl
├── test_cases/
│   ├── images/
│   │   └── imaging_lens_position_7.0_cam_0_1730496602.jpg
│   └── taxonomy_reports/
│       ├── Fragaria_GAmplicon_16S-taxonomy-and-counts.tsv
│       ├── Fragaria_GAmplicon_ITS-taxonomy-and-counts.tsv
```

## Installation

### 1. Clone the Repository
```
git clone <your-repo-url>
cd template_michael/LunarAgent
```

### 2. Set Up Python Environment
It is recommended to use Python 3.12 and a virtual environment.

```
python3 -m venv lunaragent
source lunaragent/bin/activate
```

### 3. Install Dependencies
```
pip install -r requirements.txt
```

### 4. Download Data
Ensure the required data files (CSV, TSV, images) are present in the `data/` and `test_cases/images/` directories. Example taxonomy files:
- `Fragaria_GAmplicon_16S-taxonomy-and-counts.tsv`
- `Fragaria_GAmplicon_ITS-taxonomy-and-counts.tsv`

## Running the Agent


### 1. Command Line Chat Agent
Run the main agent script:
```
python chat_agent.py
```
You will see:
```
🌕🤖 LunarAgent is ready. Type 'exit' to quit.
👤 You:
```
Type your query or anomaly description. Example:
```
👤 You: Humidity is 85% for Fragaria
```

### 2. Streamlit Dashboard
You can also run the agent with a web dashboard using Streamlit:
```
streamlit run streamlit_app.py
```
This will open a browser window with interactive tabs for:
- Agent decisions and anomaly logs
- Chat interface
- Sensor visualization

**Example Streamlit Output:**
- Tabs for Decisions, Anomaly Log, Chat, Sensor Data, and Image Monitoring
- Real-time updates and refresh buttons

Interact with the agent by entering queries in the chat tab, or view real-time anomaly detection and decision logs in other tabs.

### 2. Example Outputs

#### Environmental Anomaly
**Input:**
```
👤 You: Temperature is too high
```
**Output:**
```
[ URGENCY: HIGH ]
REASONING:
- High temperature detected for VEG_01AB sensor.
- Increased transpiration and water loss risk for plants.
ACTION:
▶  Step 1: 🔔 ALARM TRIGGERED
▶  Step 2: 🕹️ ENVIRONMENTAL CONTROL ACTIVATED
▶  Step 3: 🔄 STABILIZATION IN PROGRESS
▶  Step 4: 🔁 RESTORE TO NOMINAL
▶  Step 5: 📅 FOLLOW-UP
```

#### Pathogen Detection (Metagenomics)
**Input:**
```
👤 You: Humidity is 85% for Fragaria
```
**Output:**
```
---
Metagenomics (Amplicon, 16S and ITS) analysis triggered for Fragaria...
...Automated sample to sequencing protocol executed.
Automatic data processing completed.
...Output report of % taxonomy generated.
Screening detected taxonomies for Fragaria-specific pathogens...
Below are the taxonomy reports (only nonzero counts shown):
16S: Xanthomonas fragariae - 1267
ITS: Mycosphaerella fragariae - 721
Known Fragaria pathogens detected (count >= 10):
- Xanthomonas fragariae (count: 1267): Treatment dispensed and logged.
- Mycosphaerella fragariae (count: 721): Treatment dispensed and logged.
Follow-up metagenomics analysis scheduled for 2 weeks post treatment.
```
**Description:**
- The agent parses taxonomy files, screens for known pathogens, and only treats those above the actionable threshold (count >= 10).

#### Image-Based Anomaly
**Input:**
```
👤 You: Detect plant color anomaly
```
**Output:**
```
Image Monitoring System detected reduced green signal and increased yellow signal in the following images: imaging_lens_position_7.0_cam_0_1730496602.jpg.
This may indicate nitrogen deficiency, water stress, or pathogen infection.
Color analysis report:
imaging_lens_position_7.0_cam_0_1730496602.jpg: Green ratio=0.32, Yellow ratio=0.58
```
**Description:**
- The agent analyzes plant images for color anomalies and reports possible causes.

## Notes
- You can add more plants and their pathogens to the `plant_pathogen_db` dictionary in `chat_agent.py`.
- The agent logs all decisions and anomalies to `data/last_decision.json` and `data/decision_log.jsonl`.
- For best results, ensure all required data files are present and named correctly.

## Troubleshooting
- If you see file not found errors, check that the required data files are in the correct directories.
- For missing dependencies, run `pip install -r requirements.txt` again.

## License
MIT License
# MCPAgent: AI Anomaly Detection + Chat Agent

This project combines a real-time anomaly detection engine for CO₂ readings with a LangChain-powered AI agent capable of answering questions and querying logs via chat.

## Features
- Realtime anomaly detection from CSV stream
- Decision engine for managing alerts
- LangChain + OpenAI GPT-4 powered chat interface
- Tools for Wikipedia, DuckDuckGo search, and internal anomaly log access

