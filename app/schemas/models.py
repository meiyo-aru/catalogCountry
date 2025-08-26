from pydantic import BaseModel

# modelos pydantic dos paises
class countries_base(BaseModel):
    name: str
    likes: int
    dislikes: int

class countries_out(countries_base):
    id: int
    class Config:
        from_attributes = True

class rest_countries_model(BaseModel):
    name: dict
    population: int
    independent: bool
    region: str
    subregion: str
    languages: dict
    capital: list | None = None
    currencies: dict | None = None
    class Config:
        extra = "ignore"