# 🏎️ F1 AI Strategy Advisor

A real-time Formula 1 race strategy system that simulates IoT telemetry data and generates intelligent race recommendations using both rule-based logic and large language models (LLMs).

---

## 🚀 Overview

Formula 1 teams rely on continuous telemetry data to make high-stakes decisions during a race. This project simulates that environment by generating live telemetry (lap time, tire temperature, fuel level, and track conditions) and feeding it into a decision system.

The application combines deterministic logic with AI-driven reasoning to produce structured race strategy recommendations in real time.

The result is a cloud-deployed, interactive system that mirrors real-world race engineering workflows.

---

## ⚙️ Key Features

- Simulated IoT telemetry with realistic race progression  
- Stateful telemetry tracking across laps  
- Time-series visualization of lap time and fuel trends  
- Rules-based strategy engine for deterministic decisions  
- AI-powered strategy recommendations using Hugging Face LLMs  
- Secure API integration using Streamlit secrets and fine-grained tokens  

---

## 🏗️ Architecture

### Components

- **Data Layer**
  - Simulated telemetry stream
  - Session-based state management

- **Decision Layer**
  - Rules-based strategy engine

- **AI Layer**
  - Hugging Face LLM (Llama 3)
  - Context-aware strategy generation

- **Presentation Layer**
  - Streamlit dashboard
  - Interactive controls and visualizations

---

## 📁 Project Structure
f1-ai-strategy-advisor/
├── app/
│   └── streamlit_app.py
├── src/
│   ├── simulation.py
│   ├── rules.py
│   ├── llm.py
│   └── init.py
├── requirements.txt
└── README.md

---

## 🧰 Tech Stack

- **Frontend / UI**
  - Streamlit

- **Backend**
  - Python
  - Pandas

- **AI / LLM**
  - Hugging Face Inference API
  - Llama 3 Instruct model

- **Deployment**
  - Streamlit Community Cloud

- **Security**
  - Streamlit Secrets
  - Fine-grained API tokens

---

## 🔄 How It Works

1. Initialize race state with baseline telemetry  
2. Simulate each lap with evolving fuel, tire temperature, and lap time  
3. Maintain telemetry history for time-series analysis  
4. Generate deterministic recommendations using rules  
5. Augment strategy using an LLM with recent telemetry context  

---

## 🌐 Deployment

The application is deployed on Streamlit Community Cloud:

👉 https://f1-ai-strategy-advisor-ekkzao7ckhtbv3sfh5v4nd.streamlit.app

---
