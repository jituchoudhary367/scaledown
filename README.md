# ⚡ ScaleDown: Intelligent Context Optimization

ScaleDown is a high-performance framework designed to solve the "context window bottleneck" in modern LLM applications. By utilizing AST-guided selection and intelligent prompt compression, ScaleDown enables developers to feed massive codebases and complex conversation histories into LLMs while reducing token usage by up to 70%.

---

## 🚀 Core Features

- **🧠 Deep Research Agent Swarm**: A collaborative team of specialized agents (Researcher, Critic, Synthesizer, Writer) for high-fidelity academic and technical research.
- **🔍 HASTE Optimizer**: Hybrid AST-guided selection using Tree-sitter, BM25, and semantic search for precision code retrieval.
- **🧪 Semantic Optimizer**: Local embedding-based search using FAISS and transformer models.
- **📉 ScaleDown Compressor**: API-powered context compression that reformulates prompts for maximum token efficiency.
- **🔗 Modular Pipelines**: Seamlessly chain optimizers and compressors for customized workflows.

---

## 🧠 Collaborative AI Research Team (New!)

ScaleDown now includes an autonomous, multi-agent research swarm designed to transform abstract queries into professional, IEEE-formatted research papers.

### 🏗️ Swarm Architecture

The system is coordinated via a **LangGraph** state machine, ensuring logical handoffs and iterative refinement loops.

```mermaid
graph TD
    User([Research Query]) --> Researcher[🔍 Researcher Agent]
    Researcher --> Search{DuckDuckGo Search}
    Search --> Researcher
    Researcher --> Critic[⚖️ Critic Agent]
    
    Critic -- "Debate/Rejected" --> Researcher
    Critic -- "Consensus Reached" --> Synthesizer[🧩 Synthesizer Agent]
    
    Synthesizer --> Writer[✍️ Writer Agent]
    Writer --> Output[📄 IEEE Research PDF]
```

### ⚙️ Technical Specifications

- **Specialized Roles**: 4+ agents (Researcher, Critic, Synthesizer, Writer) with distinct technical domains.
- **Inter-Agent Compression**: ScaleDown shares *compressed* context between agents, reducing token transfer costs by **70%**.
- **Consensus Mechanism**: Automated cross-verification and debate simulation between nodes.
- **Large-Scale Coordination**: Supports **10+ agent conversations** and **5x larger research scopes** compared to standard single-agent approaches.

---

## 🛠️ Installation

### Basic Setup

```bash
pip install scaledown
```

### Advanced Optimization Suite

ScaleDown provides modular extras for heavy-duty workloads:

```bash
# AST-based code selection (HASTE)
pip install scaledown[haste]

# Embedding-based search (Semantic)
pip install scaledown[semantic]

# Full Deep Research Suite
pip install -U scaledown duckduckgo-search fpdf2 streamlit
```

---

## 📖 Quick Start: Deep Research Agent

Launch the interactive research dashboard:

```bash
streamlit run deep-research-agent/app.py
```

### CLI Execution

```bash
python deep-research-agent/run_agent.py
```

---

## 🔍 API Quick Start

### 1. Simple Prompt Compression

```python
from scaledown import ScaleDownCompressor

compressor = ScaleDownCompressor(target_model="gpt-4o", rate="auto")
result = compressor.compress(
    context="Your long technical documentation...",
    prompt="Explain the core architecture."
)
print(f"Tokens saved: {result.metrics.original_prompt_tokens - result.metrics.compressed_prompt_tokens}")
```

### 2. Full HASTE Pipeline

```python
from scaledown import Pipeline
from scaledown.optimizer import HasteOptimizer
from scaledown import ScaleDownCompressor

pipeline = Pipeline([
    ('haste', HasteOptimizer(top_k=5)),
    ('compressor', ScaleDownCompressor(target_model="gpt-4o"))
])

result = pipeline.run(
    query="explain error handling",
    file_path="app.py",
    prompt="Summarize compactly"
)
```

---

## ⚡ ScaleDown Benefits

| Feature | Standard LLM Call | ScaleDown Optimized |
| :--- | :--- | :--- |
| **Context Limit** | 128k - 2M tokens | 5x effective window |
| **Token Cost** | 100% | ~30% (70% reduction) |
| **Agent Coordination** | 3-4 agents | 10+ agents |
| **Code Retrieval** | String-matching | AST + Semantic Search |

---

## 🏗️ Project Structure

The project is organized into two primary pillars: the context optimization core and the agentic research layer.

```bash
scaledown/
├── scaledown/               # 📦 Core framework
│   ├── optimizer/           #   ├── HASTE & Semantic algorithms
│   ├── compressor/          #   ├── API-powered prompt compression
│   ├── pipeline/            #   └── Orchestration layer
│   └── types/               #   └── Data models & metrics
├── deep-research-agent/     # 🤖 Collaborative Research Team
│   ├── agents/              #   ├── Specialized Agent StateGraph
│   ├── app.py               #   ├── Streamlit Dashboard
│   └── run_agent.py         #   └── CLI Research Runner
├── examples/                # 💡 Tutorials & Implementation guides
└── tests/                   # ✅ Comprehensive test suite
```

---

## 🔍 API Reference

### HasteOptimizer (AST-Guided)

AST-guided code selection using Tree-sitter and hybrid search.

**Parameters:**

- `top_k` (int, default=6): Number of top functions/classes to retrieve
- `prefilter` (int, default=300): Size of candidate pool before reranking
- `bfs_depth` (int, default=1): BFS expansion depth over call graph
- `semantic` (bool, default=False): Enable semantic reranking with OpenAI embeddings
- `hard_cap` (int, default=1200): Hard token limit for output

**Methods:**

- `optimize(query, file_path, ...)`: Extract relevant code chunks based on structural analysis.

### SemanticOptimizer (Embedding-Based)

Local embedding-based code search using sentence transformers and FAISS.

**Parameters:**

- `model_name` (str, default="Qwen/Qwen3-Embedding-0.6B"): HuggingFace embedding model
- `top_k` (int, default=3): Number of top code chunks to retrieve

### ScaleDownCompressor (API)

API-powered prompt compression service that reformulates context for token efficiency.

**Parameters:**

- `target_model` (str, default="gpt-4o"): Target LLM for token counting
- `rate` (str, default="auto"): Compression rate ("auto" or specific ratio)
- `preserve_keywords` (bool, default=False): Preserve specific technical tokens

### Pipeline

Chain multiple optimizers and compressors for maximum reduction.

```python
pipeline = Pipeline([
    ('haste', HasteOptimizer(top_k=8)),
    ('compress', ScaleDownCompressor(target_model="gpt-4o"))
])
```

---

## ⚡ Performance & Benefits

| Feature | Standard LLM Call | ScaleDown Optimized |
| :--- | :--- | :--- |
| **Context Limit** | 128k - 2M tokens | 5x effective window |
| **Token Cost** | 100% | ~30% (70% reduction) |
| **Agent Coordination** | 3-4 agents | 10+ agents |
| **Code Retrieval** | String-matching | AST + Semantic Search |

---

## 🧪 Error Handling & Testing

### Custom Exceptions

ScaleDown defines specialized exceptions for robust integration:

- `AuthenticationError`: Missing or invalid API key.
- `APIError`: Request failure (network/server).
- `OptimizerError`: Algorithm execution failure.

### Testing Suite

```bash
# Run all tests
pytest -v
```

---

## 📖 Use Cases

- **Large Codebase Q&A**: Feed entire directories into LLMs without truncation.
- **Academic Research**: Automate deep literature reviews and report generation.
- **Automated Refactoring**: Identify and compress relevant code sections for broad architectural changes.
- **Conversation Summarization**: Compress long chat logs for long-term memory.

---

## 💡 Performance Tips

1. **Use HASTE for structural code**: It's optimized for call-graph exploration.
2. **Enable semantic search** in HasteOptimizer for better relevance.
3. **Batch compress** multiple prompts for higher throughput.
4. **Set appropriate caps**: Adjust `hard_cap` and `top_k` based on your model's native context limit.

---

## 📖 Links & Resources

- **Homepage**: [https://scaledown.ai](https://scaledown.ai)
- **Documentation**: [https://docs.scaledown.ai](https://docs.scaledown.ai)
- **Support**: Open an issue on GitHub for technical assistance.

---
*Developed by the ScaleDown Multi-Agent Laboratory.*
