from rich.console import Console
from prompts.metadata_prompt import METADATA_PROMPT

console = Console()

def generate_metadata(text, llm):
    chain = METADATA_PROMPT | llm
    result = chain.invoke({"text": text})
    
    if hasattr(result, "content"):
        result = result.content

    console.log(f"[blue]LLM Output:[/blue] {result}")

    try:
        return result
    except Exception as e:
        console.log(f"[red]Failed to parse metadata:[/red] {e}")
        return None