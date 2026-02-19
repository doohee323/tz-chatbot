"""RAG chains: retriever + prompt + LLM.

Same system prompt as Dify workflow (dify/cointutor/Question Classifier + Knowledge + Chatbot .yml).
Uses same RAG DB/index via RAG Backend -> Qdrant so results are comparable to Dify.
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.config import Settings
from app.llm_helper import get_llm
from app.retrievers import RagApiRetriever

# Exact text from Dify LLM node prompt_template (both after_sales and products branches)
SYSTEM_PROMPT = """Use the following context as your learned knowledge, inside <context></context> XML tags.

<context>

{context}

</context>

When answer to user:

- If you don't know, just say that you don't know.
- If you don't know when you are not sure, ask for clarification.
Avoid mentioning that you obtained the information from the context.
And answer according to the language of the user's question."""


def _format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain(settings: Settings, collection: str):
    """Build RAG chain: retriever -> context -> LLM."""
    retriever = RagApiRetriever(
        rag_url=settings.rag_backend_url,
        collection=collection,
        top_k=settings.rag_top_k,
    )
    llm = get_llm(settings)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{query}"),
    ])
    chain = (
        {"context": retriever | _format_docs, "query": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain
