from pydantic import BaseModel

class DocumentMetadata(BaseModel):
    title: str
    summary: str
    topics: list[str]
    entities: list[str]