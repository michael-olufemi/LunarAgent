# AI Agent for a Simulated Lunar Agriculture Pod

This project provides an autonomous AI agent designed to manage and monitor a simulated lunar agriculture pod. The agent integrates environmental sensor data, plant image analysis, and metagenomics workflows to ensure optimal plant health and system stability in a closed lunar environment.

The agent continuously monitors environmental conditions such as temperature, humidity, and CO₂ levels using sensor data. When anomalies are detected, it can autonomously trigger corrective actions, such as activating fans or adjusting atmospheric composition, to maintain optimal growing conditions for plants.

In addition to environmental monitoring, the agent analyzes plant images to detect color anomalies, such as yellowing or loss of green signal. These visual cues can indicate nutrient deficiencies, water stress, or disease. The agent automatically flags problematic images and generates detailed color analysis reports to assist with diagnostics.

For pathogen detection, the agent processes metagenomics sequencing data (16S and ITS amplicon files) to screen for plant pathogens. It identifies actionable threats, recommends treatments, and logs all actions taken. The agent can also query scientific literature and databases for information on detected pathogens or environmental issues, providing users with relevant research and context.

Users can interact with the agent through a command-line chat interface or a Streamlit dashboard. The agent responds to queries, provides anomaly detection results, reviews logs, and offers actionable recommendations. All decisions and anomalies are logged for traceability and follow-up.

This project is intended for research, simulation, and prototyping of autonomous agricultural management systems for space habitats. Its modular design allows for easy extension to new ssensors, plant species, and workflows.

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
│   └── taxonomy_reports/
│       ├── Fragaria_GAmplicon_16S-taxonomy-and-counts.tsv
│       ├── Fragaria_GAmplicon_ITS-taxonomy-and-counts.tsv
```

## Installation

### 1. Clone the Repository
```
git clone https://github.com/michael-olufemi/LunarAgent.git
cd LunarAgent/
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
Ensure the required data files (CSV, TSV, images) are present in the `data/` directory, and in the `test_cases/images/ and test_cases/taxonomy_reports` directories to run the test cases on the agent. Example taxonomy files:
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
- Agent decisions
- Anomaly logs
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
