# ScaleDown: Technical Documentation & Architecture Deep Dive

Welcome to the comprehensive technical manual for **ScaleDown**. This document provides an in-depth analysis of the system architecture, the Agentic Research Swarm, and the core optimization algorithms that enable high-efficiency LLM interactions.

---

## 1. High-Level Architecture

ScaleDown is built as a modular framework for context optimization. It bridges the gap between massive local datasets (or codebases) and the finite context windows of Large Language Models.

### 🏗️ System Components

- **The Core (`scaledown/`)**: Contains the optimization engine, including HASTE (AST-guided), Semantic (vector-based), and the API-powered Compressor.
- **Deep Research Agent (`deep-research-agent/`)**: An application layer utilizing the ScaleDown core to perform complex, multi-step research tasks using a swarm of autonomous agents.
- **Pipeline Orchestration**: A flexible chaining mechanism that allows developers to compose custom sequences of optimizers and compressors.

---

## 2. Collaborative AI Research Team (Agent Swarm)

The Deep Research Agent is not a single prompt; it is a **LangGraph-driven state machine** that coordinates multiple specialized agents.

### 🤖 Agent Roles & Responsibilities

1. **🔍 Researcher**: Gathers empirical data using real-time search tools (DuckDuckGo). It focuses on evidence retrieval and technical specifications.
2. **⚖️ Critic**: Acts as a senior reviewer. It identifies hallucinations, challenges weak claims, and enforces a "confidence threshold" (0.7).
3. **🧩 Synthesizer**: Merges verified insights from the Critic and Researcher into a cohesive theoretical framework. It utilizes the ScaleDown Core to handle massive context during synthesis.
4. **✍️ Writer**: Transforms the synthesized framework into a professional academic paper, following IEEE formatting guidelines.

### 🔄 The Iterative Loop

The system employs a cyclic workflow:

- **Researcher** gather data -> **Critic** reviews.
- If **Confidence < Threshold**, the **Researcher** is re-triggered with specific feedback from the Critic.
- Once **Confidence >= Threshold**, the system proceeds to **Synthesizer**.

---

## 3. ScaleDown Core Algorithms

### 🔍 HASTE (Hybrid AST-guided Selection Engine)

HASTE is designed for precision code retrieval.

- **Parsing**: Uses Tree-sitter to build a structural map of the codebase.
- **BFS Expansion**: When a relevant function is found, HASTE performs a Breadth-First Search on the call graph to include its dependencies, ensuring the LLM has the full context of "how it's called."
- **Hybrid Search**: Combines BM25 lexical search with optional semantic reranking.

### 📉 ScaleDown Compressor

Unlike standard "summarizers," the Compressor is an LLM-powered rewrite engine.

- **Information Density**: It reformulates long context into a high-density "token-efficient" format.
- **Preservation**: It can be configured to preserve specific technical keywords or segments while pruning redundant filler.
- **API Optimized**: Designed to work as a pre-processing step to minimize input costs on expensive models like GPT-4o or Claude 3.5 Sonnet.

---

## 4. Deployment & Integration

### Local Deployment

```bash
streamlit run deep-research-agent/app.py
```

### Streamlit Cloud Deployment

- **Repository**: GitHub connection to `jituchoudhary367/scaledown`.
- **Requirements**: Handled via `requirements.txt` (clean, flat list format).
- **Secrets Management**: requires `OPENROUTER_API_KEY` and `SCALEDOWN_API_KEY` in the Streamlit Cloud "Secrets" section.

### Error Handling Protocols

ScaleDown implements a hierarchical exception model:

- `ScaleDownError`: Base class for all framework issues.
- `AuthenticationError`: Raised on API key failures.
- `OptimizerError`: Raised when local parsing or retrieval fails.

---
*Documentation Version 1.1 - Part of the ScaleDown Multi-Agent Laboratory.*
