"""RAG chains: retriever + prompt + LLM. Same system prompt as Dify workflow."""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.config import Settings
from app.retrievers import RagApiRetriever


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
    llm = ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.gemini_api_key,
        temperature=settings.temperature,
        max_output_tokens=settings.max_tokens,
    )
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
