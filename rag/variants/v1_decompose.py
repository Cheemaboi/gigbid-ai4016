from rag.retriever import retrieve
def run(requirements, corpus): return retrieve(requirements, corpus, variant="v1_decompose")
