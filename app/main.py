afrom typing import List
import requests
from app.models.models import countries
from app.db.connect_db import get_db
from app.api.create_app import app
from app.api.create_app import Session, Depends
from app.schemas.models import countries_out, rest_countries_model
from fastapi import status, HTTPException

# Endpoint para buscar país pelo nome, retornando o modelo pydantic countries_out
@app.get("/paises/buscar", status_code=status.HTTP_200_OK, response_model=rest_countries_model)
async def buscar(name: str, db: Session = Depends(get_db)):
    
    response = requests.get('https://restcountries.com/v3.1/name/' + name.strip() + '?fullText=true') # faz a requisição para a API externa
    
    # Se o país não for encontrado na API externa, retorna 404
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Falha na requisição.")        
    
    
    model = rest_countries_model.model_validate(response.json()[0])  # valida os dados da api externa, excluindo os campos que não existem no modelo pydantic
    
    data = db.query(countries).filter(countries.name == name.strip()).first() # busca o país no banco de dados
    
    if data is None:
        setattr(model, 'likes', 0)      # se o país não existir no banco, define likes e dislikes como 0
        setattr(model, 'dislikes', 0)
    else:
        setattr(model, 'likes', data.likes)        # se o país existir no banco, define likes e dislikes com os valores do banco
        setattr(model, 'dislikes', data.dislikes)
        
    return model


# Endpoint para listar os 10 paises mais populosos
@app.get("/paises/top10", status_code=status.HTTP_200_OK)
async def top10(db: Session = Depends(get_db)):
    
    response = requests.get('https://restcountries.com/v3.1/all?fields=name,population,independent,region,subregion,languages,capital,currencies') # faz a requisição para a API externa
    
    # validacao de erro na requisição
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Falha na requisição.")        
    
    # ordena os países pela população em ordem decrescente e pega os 10 primeiros
    sorted_countries = sorted(
        response.json(),
        key=lambda pais: pais['population'], # ordena pela população
        reverse=True  # 'reverse=True' para ordenar do maior para o menor
    )[0:10]
    
    for country in sorted_countries:
        model = rest_countries_model.model_validate(country)
        data = db.query(countries).filter(countries.name == model.name['common']).first() # busca o país no banco de dados
        
        if data is None:
            setattr(model, 'likes', 0)      # se o país não existir no banco, define likes e dislikes como 0
            setattr(model, 'dislikes', 0)
        else:
            setattr(model, 'likes', data.likes)        # se o país existir no banco, define likes e dislikes com os valores do banco
            setattr(model, 'dislikes', data.dislikes)
        
        
    return sorted_countries
