from pydantic import BaseModel

# modelos pydantic dos paises
class rest_countries_model(BaseModel):
    name: dict
    population: int
    independent: bool
    region: str
    subregion: str
    continents: list
    languages: dict
    capital: list | None = None
    currencies: dict | None = None
    likes: int = 0
    dislikes: int = 0
    class Config:
        extra = "ignore"
        
class paises_avaliar(BaseModel):
    name: str
    rating: str
    
