from langchain_core.prompts import PromptTemplate

METADATA_PROMPT = PromptTemplate.from_template(
    """
    You are a metadata generator. Given the following text, extract the metadata as JSON:
    - Title: a concise title
    - Summary: 2–3 sentence description
    - Topics: list of key themes
    - Entities: list of named entities (people, organizations, locations)

    Text:
    {text}

    Return valid JSON only.
    """
    )