from pydantic import BaseModel
from uuid import UUID

class Blog(BaseModel):
    user_id: UUID
    blog_title: str
    blog_text: str