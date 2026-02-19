"""Question classifier: 3-way (after_sales, products, other).

Mirrors Dify workflow: dify/cointutor/Question Classifier + Knowledge + Chatbot .yml
Same class descriptions and labels so behavior matches when chat-gateway uses chat-inference instead of Dify.
"""
import logging
from typing import Callable
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from app.config import Settings
from app.llm_helper import get_llm

logger = logging.getLogger("chat_inference")

# Same as Dify Question Classifier node; added hint so pricing/fees (e.g. 수수료) go to products
CLASSIFIER_SYSTEM = (
    "You classify user questions into exactly one of these labels:\n"
    "- {after_sales}: Question related to after sales\n"
    "- {products}: Questions about how to use products. Pricing, fees, and cost (e.g. 수수료, subscription) also count as products.\n"
    "- {other}: Other questions\n\n"
    "Reply with ONLY one word: {after_sales}, {products}, or {other}. No explanation."
)


def build_classifier(settings: Settings) -> Callable[[str], str]:
    """Classify user query into after_sales, products, or other. Returns label string."""
    llm = get_llm(settings)
    prompt = ChatPromptTemplate.from_messages([
        ("system", CLASSIFIER_SYSTEM),
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
        raw = (result or "").strip()
        label = raw.lower()
        logger.info("Classifier raw reply: %r", raw)
        if settings.class_after_sales in label:
            return settings.class_after_sales
        if settings.class_products in label:
            return settings.class_products
        return settings.class_other

    return classify
