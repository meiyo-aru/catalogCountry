from typing import Any
from pydantic import BaseModel, field_validator

# modelos pydantic dos paises
class rest_countries_model(BaseModel):
    name: str
    population: int
    region: str
    likes: int = 0
    dislikes: int = 0
    
    @field_validator('name', mode='before')
    @classmethod
    def extract_name(cls, v: Any):
        if isinstance(v, dict) and 'common' in v:
            return v['common']
        return v

    
    class Config:
        extra = "ignore"
        
class rating_model(BaseModel):
    name: str
    rating: str
    
class rating_response_model(BaseModel):
    name: str
    total_votes: int
    status: str