from langgraph.graph import StateGraph, END
from typing import TypedDict, List , Any
import networkx as nx

class State(TypedDict):
    query:str
    documents:List[str]
    retrieved_chunks:List[str]
    graph_context:List[str]
    answer:str

DOCS = [
    "Elon Musk founded SpaceX in 2002.",
    "SpaceX developed the Falcon 9 rocket for NASA missions.",
    "NASA's Artemis program aims to return humans to the Moon.",
    "Elon Musk also co-founded Tesla which makes electric cars.",
]
def build_graph(docs):
    G=nx.DiGraph()
    rules=[
        ("Elon Musk","SpaceX","founded"),
        ("Elon Musk","Tesla","co-founded"),
        ("SpaceX","Falcon 9","developed"),
        ("SpaceX","NASA","works_with"),
        ("NASA","Moon","targets"),

    ]
    for s, o , r in rules:
        G.add_edge(s,o, relation=r)
    return G

KG=build_graph(DOCS)
print("Graph edges:", list(KG.edges(data=True)))

def retrieve_chunks(query:str)->List[str]:
    return[doc for doc in DOCS if any(
        word.lower() in doc.lower()
        for word in query.split()
        
    )]
def retrieve_chunks(query: str) -> List[str]:
    # Simple keyword match — in real life this is FAISS vector search
    return [doc for doc in DOCS if any(
        word.lower() in doc.lower() 
        for word in query.split()
    )]

def retrieve_graph_context(query: str) -> List[str]:
    context = []
    query_lower = query.lower()
    
    for node in KG.nodes():
        if node.lower() in query_lower:
            # 1-hop: outgoing
            for _, neighbor, data in KG.out_edges(node, data=True):
                context.append(f"{node} --[{data['relation']}]--> {neighbor}")
            # 1-hop: incoming  
            for predecessor, _, data in KG.in_edges(node, data=True):
                context.append(f"{predecessor} --[{data['relation']}]--> {node}")
            # 2-hop
            for _, neighbor in KG.out_edges(node):
                for _, hop2, data in KG.out_edges(neighbor, data=True):
                    context.append(f"{neighbor} --[{data['relation']}]--> {hop2}")
    return context
def node_retrieve(state: State) -> dict:
    chunks = retrieve_chunks(state["query"])
    graph_ctx = retrieve_graph_context(state["query"])
    print(f"\nChunks found: {len(chunks)}")
    print(f"Graph context found: {len(graph_ctx)}")
    return {"retrieved_chunks": chunks, "graph_context": graph_ctx}

def node_answer(state: State) -> dict:
    chunks_text  = "\n".join(state["retrieved_chunks"])
    graph_text   = "\n".join(state["graph_context"])
    
    # Simulated answer (replace with real LLM call when you add API key)
    answer = f"""
    Based on text chunks:
    {chunks_text}
    
    Based on graph relationships:
    {graph_text}
    """
    return {"answer": answer}
workflow = StateGraph(State)

workflow.add_node("retrieve", node_retrieve)
workflow.add_node("answer",   node_answer)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "answer")
workflow.add_edge("answer", END)

app = workflow.compile()

# Run it
result = app.invoke({
    "query": "What company connected to Elon Musk works with NASA?",
    "documents": DOCS,
    "retrieved_chunks": [],
    "graph_context": [],
    "answer": ""
})

print("\n=== FINAL ANSWER ===")
print(result["answer"])


    

