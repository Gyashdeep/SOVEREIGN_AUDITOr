# Sovereign Auditor
**Cryptographically Verifiable AI Governance Infrastructure.**

## Overview
The Sovereign Auditor is a production-grade AI framework designed for high-stakes enterprise environments. It shifts AI from "predictive chatbots" to "governed, deterministic infrastructure" by integrating model routing, cryptographic audit trails, and hard-coded safety circuit breakers.

## Key Features
- **Poly-Model Routing:** Dynamically routes requests between high-speed LPUs (Groq/Llama) and deep-reasoning frontier models (Claude) based on risk profiles.
- **Cryptographic Evidence Ledger:** All decisions are hash-chained with HMAC-SHA256 signatures, ensuring immutable and verifiable audit trails.
- **Human-in-the-Loop (HITL) Governance:** High-risk actions are automatically gated until a human operator provides a digital handshake.
- **Hard-Coded Circuit Breakers:** Deterministic shutdown triggers prevent AI execution when safety thresholds are violated.

## Getting Started
1. **Clone:** `git clone https://github.com/your-username/sovereign-auditor.git`
2. **Install:** `pip install -r requirements.txt`
3. **Configure:** Create a `.env` file based on `.env.example` with your API keys.
4. **Launch:** `streamlit run app.py`

## Compliance
This system is built for environments requiring SOC2/GDPR compliance. It provides real-time integrity verification of all decision-making processes.
