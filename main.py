from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(title="API de Chamados")

class ChamadoEntrada(BaseModel):
    titulo: str
    descricao: str
    prioridade: str

chamados = []

@app.get("/")
def inicio():
    return {"mensagem": "API de Chamados ativa"}

@app.get("/chamados")
def listar_chamados():
    return chamados

@app.post("/chamados", status_code=status.HTTP_201_CREATED)
def criar_chamado(dados: ChamadoEntrada):
    chamado = {
        "id": len(chamados) + 1,
        **dados.model_dump(),
        "status": "aberto"
    }
    chamados.append(chamado)
    return chamado

@app.get("/chamados/{chamado_id}")
def buscar_chamado(chamado_id: int):
    for chamado in chamados:
        if chamado["id"] == chamado_id:
            return chamado
    raise HTTPException(
        status_code=404,
        detail="Chamado não encontrado"
    )
