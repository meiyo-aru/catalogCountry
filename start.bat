@echo off
rem Cria um ambiente virtual do python, o ativa e inicia o Uvicorn
start "Uvicorn Server" cmd /k "python -m venv venv && call .\venv\scripts\activate && uvicorn app.main:app --reload --reload-dir . --host localhost --port 8000"

echo Todos os processos iniciados. Feche as janelas para parar.