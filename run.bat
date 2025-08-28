@echo off
rem Define o nome da pasta do ambiente virtual
set VENV_FOLDER=venv

rem Verifica se o ambiente virtual já existe
if not exist %VENV_FOLDER%\ (
    echo Criando ambiente virtual...
    python -m venv %VENV_FOLDER%
)

rem Ativa o ambiente virtual
echo Ativando o ambiente virtual...
call .\%VENV_FOLDER%\Scripts\activate

rem Instala as dependências listadas no requirements.txt
echo Instalando dependencias...
pip install -r requirements.txt

rem Inicia o servidor Uvicorn em uma nova janela de terminal
start "Uvicorn Server" cmd /k "uvicorn app.main:app --reload --reload-dir . --host localhost --port 8000"

echo.
echo Servidor Uvicorn iniciado em uma nova janela.
exit