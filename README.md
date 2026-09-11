# Formulário HTML + FastAPI + Pydantic + SQLite

Exemplo didático no qual:

- o formulário HTML coleta os dados;
- o JavaScript envia JSON com `fetch`;
- o Pydantic valida o contrato somente no back-end;
- o SQLite mantém os registros;
- a resposta da API é impressa na página.

## Como executar

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Depois, abra `http://127.0.0.1:8000`.

