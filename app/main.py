from typing import List
import requests
from app.models.models import countries
from app.db.connect_db import get_db
from app.api.create_app import app
from app.api.create_app import Session, Depends
from app.schemas.models import countries_base, countries_out, paises_avaliar, rest_countries_model
from fastapi import status, HTTPException

# Endpoint para buscar país pelo nome, retornando o modelo pydantic countries_out
@app.get("/paises/buscar", status_code=status.HTTP_200_OK, response_model=rest_countries_model)
async def buscar(name: str, db: Session = Depends(get_db)):
    
    response = requests.get('https://restcountries.com/v3.1/name/' + name.strip() + '?fullText=true') # faz a requisição para a API externa
    
    # Se o país não for encontrado na API externa, retorna 404
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="País não encontrado.")        

    elif response.status_code != 200:
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
@app.get("/paises/top10", status_code=status.HTTP_200_OK, response_model=List[rest_countries_model])
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
    
    for country in sorted_countries: # para cada país na lista, consulta o banco de dados para obter likes e dislikes
        model = rest_countries_model.model_validate(country) # valida os dados da api externa, excluindo os campos que não existem no modelo pydantic
        
        data = db.query(countries).filter(countries.name == model.name['common']).first() # busca o país no banco de dados
        if data is None:
            setattr(model, 'likes', 0)      # se o país não existir no banco, define likes e dislikes como 0
            setattr(model, 'dislikes', 0)
        else:
            setattr(model, 'likes', data.likes)        # se o país existir no banco, define likes e dislikes com os valores do banco
            setattr(model, 'dislikes', data.dislikes)
        
        sorted_countries[sorted_countries.index(country)] = model # atualiza a lista com o modelo pydantic convertido em dicionário
        
    return sorted_countries

# Endpoint para avaliar os países
@app.post("/paises/avaliar", status_code=status.HTTP_200_OK)
async def avaliar(avaliacao: paises_avaliar, db: Session = Depends(get_db)):
    
    response = requests.get('https://restcountries.com/v3.1/name/' + avaliacao.name.strip() + '?fields=name') # faz a requisição para a API externa
    
    # validacao de erro na requisição
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail="País não encontrado.")
    elif response.status_code != 200:
        raise HTTPException(status_code=400, detail="Falha na requisição.")        

    data = db.query(countries).filter(countries.name == avaliacao.name.strip()).first() # busca o país no banco de dados
    
    # se o país nao existir no banco, cria um novo registro com 1 like ou 1 dislike dependendo da avaliação
    if data is None:
        data = countries(name=avaliacao.name.strip(), likes=(1 if avaliacao.rating == "curti" else 0), dislikes=(1 if avaliacao.rating == "não curti" else 0))
        
        db.add(data) # adiciona o novo país na sessão
        db.flush() # forca a execução do insert
        db.commit() # salva as alterações no banco de dados
        db.refresh(data)  # atualiza o objeto com os dados do banco de dados

    else:
        if avaliacao.rating == "curti":
            setattr(data, "likes", data.likes + 1) # incrementa 1 no campo likes
        elif avaliacao.rating == "não curti":
            setattr(data, "dislikes", data.dislikes + 1) # incrementa 1 no campo dislikes
        else:
            raise HTTPException(status_code=400, detail="Avaliação inválida. Use 'curti' ou 'não curti'.")
    
        db.commit() # salva as alterações no banco de dados
        db.refresh(data) # atualiza o objeto com os dados do banco de dados
        
    return data
