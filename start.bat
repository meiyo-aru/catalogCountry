@echo off
rem Ativa o ambiente virtual no script atual
call .\venv\scripts\activate

rem Inicia o Uvicorn em uma nova janela de terminal, ativando o venv lá
start "Uvicorn Server" cmd /k "call .\venv\scripts\activate && uvicorn app.main:app --reload --reload-dir . --host localhost --port 8000"

echo Todos os processos iniciados. Feche as janelas para parar.