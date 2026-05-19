# Graph RAG with LangGraph

A Graph RAG pipeline built with LangGraph that combines keyword search with knowledge graph traversal to answer multi-hop questions.

## What is Graph RAG?

Standard RAG finds text chunks similar to your query. Graph RAG also traverses a knowledge graph to find how entities connect, enabling multi-hop reasoning.

| | Standard RAG | Graph RAG |
|---|---|---|
| Storage | Vector embeddings | Vectors + Knowledge graph |
| Retrieval | Similarity search | Similarity + Graph traversal |
| Multi-hop questions | Misses connections | Finds full chain |

### Example

**Query:** "What company connected to Elon Musk works with NASA?"

**Standard RAG:** returns chunks that mention NASA — misses the Elon → SpaceX → NASA chain.

**Graph RAG:** traverses `Elon Musk --[founded]--> SpaceX --[works_with]--> NASA` and returns the full relationship chain.

## Tech Stack

- **LangGraph** — pipeline orchestration (nodes + edges + state)
- **NetworkX** — knowledge graph storage and traversal
- **Python 3.12**

## Project Structure

```
graph-rag-langgraph/
├── graph_rag.py      # full pipeline
├── README.md
└── venv/             # virtual environment
```

## Setup

```bash
# Create and activate virtual environment
python -m venv venv

# Mac/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# Install dependencies
pip install langgraph langchain langchain-openai openai networkx
```

## How It Works

### 1. State
A shared dictionary passed between every node in the pipeline.

```python
class State(TypedDict):
    query: str
    documents: List[str]
    retrieved_chunks: List[str]
    graph_context: List[str]
    answer: str
```

### 2. Knowledge Graph
Entities (nodes) and relationships (edges) stored in NetworkX.

```
Elon Musk --[founded]-->    SpaceX
Elon Musk --[co-founded]--> Tesla
SpaceX    --[developed]-->  Falcon 9
SpaceX    --[works_with]--> NASA
NASA      --[targets]-->    Moon
```

### 3. LangGraph Pipeline
Two nodes wired together:

```
retrieve → answer → END
```

- `retrieve` node — runs keyword search + graph traversal
- `answer` node — combines both results into a final answer

## Pipeline Flow

```
User query
    │
    ▼
retrieve node
    ├── keyword search  → matching text chunks
    └── graph traversal → relationship chains
    │
    ▼
answer node
    └── combines chunks + graph context → final answer

## Running

```bash
python graph_rag.py
```

Expected output:

```
Graph edges: [('Elon Musk', 'SpaceX', {'relation': 'founded'}), ...]
Chunks found: 3
Graph context found: 6

=== FINAL ANSWER ===
Based on text chunks:
Elon Musk founded SpaceX in 2002.
SpaceX developed the Falcon 9 rocket for NASA missions.
Elon Musk also co-founded Tesla which makes electric cars.

Based on graph relationships:
Elon Musk --[founded]--> SpaceX
Elon Musk --[co-founded]--> Tesla
SpaceX --[developed]--> Falcon 9
SpaceX --[works_with]--> NASA
NASA --[targets]--> Moon
```

