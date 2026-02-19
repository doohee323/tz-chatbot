"""Question classifier: 3-way (after_sales, products, other). Same labels as Dify workflow."""
from typing import Callable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.config import Settings


def build_classifier(settings: Settings) -> Callable[[str], str]:
    """Classify user query into after_sales, products, or other. Returns label string."""
    llm = ChatGoogleGenerativeAI(
        model=settings.llm_model,
        google_api_key=settings.gemini_api_key,
        temperature=settings.temperature,
        max_output_tokens=settings.max_tokens,
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You classify user questions into exactly one of these labels:\n"
         "- {after_sales}: Question related to after sales (SOP, support, refund, etc.)\n"
         "- {products}: Questions about how to use products (features, usage, guide)\n"
         "- {other}: Other questions not fitting the above\n\n"
         "Reply with ONLY one word: {after_sales}, {products}, or {other}. No explanation."),
        ("human", "{query}"),
    ])
    chain = prompt | llm | StrOutputParser()

    def classify(query: str) -> str:
        result = chain.invoke({
            "query": query,
            "after_sales": settings.class_after_sales,
            "products": settings.class_products,
            "other": settings.class_other,
        })
        label = (result or "").strip().lower()
        if settings.class_after_sales in label:
            return settings.class_after_sales
        if settings.class_products in label:
            return settings.class_products
        return settings.class_other

    return classify
