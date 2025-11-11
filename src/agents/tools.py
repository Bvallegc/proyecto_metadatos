from langchain.tools import tool

def make_retrieve_context_tool(vectordb):
    @tool
    def retrieve_context(query: str) -> str:
        """Retrieve information to help answer a query."""
        retrieved_docs = vectordb.similarity_search(query, k=2)
        serialized = "\n\n".join(
            (f"Source: {doc.metadata}\nContent: {doc.page_content}")
            for doc in retrieved_docs
        )
        return serialized

    return retrieve_context
