# 🌍 Catálogo de Países com Avaliação

Este projeto é uma **API** desenvolvida em Python com FastAPI, com o objetivo de consumir dados da [REST Countries](https://restcountries.com) e disponibilizar endpoints para listagem, busca e avaliação de países.  

---

## 🚀 Funcionalidades

- **Listar os 10 países mais populosos**
  - Endpoint: `GET /paises/top10`
  - Retorna os 10 países com maior população no formato JSON.

- **Buscar país pelo nome**
  - Endpoint: `GET /paises/buscar?nome=brasil`
  - Retorna os dados do país pesquisado 

- **Avaliar um país (curti / não curti)**
  - Endpoint: `POST /paises/avaliar`
  - Corpo da requisição (JSON):  
    ```json
    {
      "name": "Brasil",
      "rating": "curti"
    }
    ```
  - Retorno esperado:
    ```json
    {
      "name": "Brasil",
      "status": "200 OK",
      "total_votes": 42
    }
    ```

---

## 🛠 Tecnologias Utilizadas

- Linguagem: **Python**
- Framework: **FastAPI (Python)**  
- Banco de Dados: **Supabase** (PostgreSQL)  
- API Consumida: [REST Countries](https://restcountries.com)

---

## 🗄 Banco de Dados (Supabase)

Para salvar as avaliações, é necessário:  

1. Criar um **projeto no [Supabase](https://supabase.com/)**.  
2. Dentro do Supabase, criar uma tabela chamada `countries` com a seguinte estrutura:  

```sql
CREATE TABLE countries (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    likes int4,
    dislikes int4
);
```
3. Adicionar as informações de conexão do banco em um arquivo .env no diretório raiz
