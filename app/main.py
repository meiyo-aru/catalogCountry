from typing import List
import requests
from app.models.models import countries
from app.db.connect_db import get_db
from app.api.create_app import app
from app.api.create_app import Session, Depends
from app.schemas.models import rating_model, rating_response_model, rest_countries_model
from fastapi import status, HTTPException

def send_request(url: str, parameters: dict={}, timeout: int = 60) -> List:
    try:
        response = requests.get(url=url, params=parameters, timeout=timeout) # faz a requisição para a API externa
        response.raise_for_status() # Levanta um HTTPError se a resposta for um sucesso
        data = response.json()
    except requests.exceptions.ConnectionError as e:
        # Lida com erros de conexão
        raise Exception(f"Erro de Conexão: Verifique sua conexão com a internet. Detalhes: {e}")
    except requests.exceptions.Timeout as e:
        # Lida com erros de tempo limite da requisição
        raise Exception(f"Erro de Tempo Limite: O servidor demorou demais para responder. Detalhes: {e}")
    except requests.exceptions.HTTPError as e:
        # Lida com erros HTTP
        raise HTTPException(status_code=e.response.status_code, detail=f"Erro HTTP: O servidor retornou um erro. Detalhes: {e}")

    return data

def set_rating(data, model):
    if data is None:
        setattr(model, 'likes', 0)      # se o país não existir no banco, define likes e dislikes como 0
        setattr(model, 'dislikes', 0)
    else:
        setattr(model, 'likes', data.likes)        # se o país existir no banco, define likes e dislikes com os valores do banco
        setattr(model, 'dislikes', data.dislikes)
        

# Endpoint para buscar país pelo nome, retornando o modelo pydantic rest_countries_model
@app.get("/paises/buscar", status_code=status.HTTP_200_OK, response_model=rest_countries_model)
async def find(name: str, db: Session = Depends(get_db)):
    response = send_request(url='https://restcountries.com/v3.1/name/' + name.strip(), parameters={"fullText": "true"})[0]  # chama a funcao de envio de requisicao e pega o primeiro elemento da lista
    model = rest_countries_model.model_validate(response)  # valida os dados da api externa, excluindo os campos que não existem no modelo pydantic
    
    data = db.query(countries).filter(countries.name == model.name).first() # busca o país no banco de dados
    set_rating(data, model)
        
    return model


# Endpoint para listar os 10 paises mais populosos
@app.get("/paises/top10", status_code=status.HTTP_200_OK, response_model=List[rest_countries_model])
async def top10(db: Session = Depends(get_db)):
    response = send_request(url='https://restcountries.com/v3.1/all', parameters={"fields": "name,population,region"}) # chama a funcao de envio de requisicao
     
    # ordena os países pela população em ordem decrescente e pega os 10 primeiros
    sorted_countries = sorted(
        response,
        key=lambda pais: pais['population'], # ordena pela população
        reverse=True  # 'reverse=True' para ordenar do maior para o menor
    )[0:10]
    
    for country in sorted_countries: # para cada país na lista, consulta o banco de dados para obter likes e dislikes
        model = rest_countries_model.model_validate(country) # valida os dados da api externa, excluindo os campos que não existem no modelo pydantic
        
        data = db.query(countries).filter(countries.name == model.name).first()# busca o país no banco de dados    
        set_rating(data, model)

        sorted_countries[sorted_countries.index(country)] = model # atualiza a lista com o modelo pydantic convertido em dicionário
        
    return sorted_countries

# Endpoint para avaliar os países
@app.post("/paises/avaliar", status_code=status.HTTP_200_OK)
async def rate(avaliacao: rating_model, db: Session = Depends(get_db)):
    
    response = send_request(url='https://restcountries.com/v3.1/name/' + avaliacao.name.strip(), parameters={"fields":"name,population,region"})[0] # chama a funcao de envio de requisicao e pega o primeiro elemento da lista (RestCountries sempre retorna uma lista)
    model = rest_countries_model.model_validate(response)
    data = db.query(countries).filter(countries.name == model.name).first() # busca o país no banco de dados
    
    # se o país nao existir no banco, cria um novo registro com 1 like ou 1 dislike dependendo da avaliação
    if data is None:
        data = countries(name=model.name, likes=(1 if avaliacao.rating == "curti" else 0), dislikes=(1 if avaliacao.rating == "não curti" else 0))
        
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

    return rating_response_model(name=getattr(data, 'name'), total_votes=getattr(data, 'dislikes') + getattr(data, 'likes'), status="200 OK")
