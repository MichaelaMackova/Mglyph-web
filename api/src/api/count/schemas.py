from pydantic import BaseModel

class CountDTO(BaseModel):
    count: int