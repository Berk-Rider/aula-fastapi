"""Aplicação didática: formulário HTML, FastAPI, Pydantic e SQLite."""

import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
BANCO = BASE_DIR.parent / "chamados.db"


def conectar() -> sqlite3.Connection:
    """Cria uma conexão e permite acessar as colunas pelo nome."""
    conexao = sqlite3.connect(BANCO)
    conexao.row_factory = sqlite3.Row
    return conexao


def preparar_banco() -> None:
    """Cria a tabela automaticamente na primeira execução."""
    with conectar() as conexao:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS chamados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno TEXT NOT NULL,
                email TEXT NOT NULL,
                assunto TEXT NOT NULL,
                descricao TEXT NOT NULL,
                prioridade TEXT NOT NULL,
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


class ChamadoEntrada(BaseModel):
    """Contrato validado exclusivamente no servidor."""

    aluno: str = Field(min_length=3, max_length=80)
    email: str = Field(min_length=5, max_length=120, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    assunto: str = Field(min_length=3, max_length=100)
    descricao: str = Field(min_length=10, max_length=500)
    prioridade: str = Field(pattern=r"^(baixa|media|alta)$")


class ChamadoSaida(ChamadoEntrada):
    id: int
    criado_em: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    preparar_banco()
    yield


app = FastAPI(title="Aplicativo de Chamados", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/", include_in_schema=False)
def abrir_formulario():
    """Entrega o formulário ao navegador."""
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/api/chamados", response_model=ChamadoSaida, status_code=status.HTTP_201_CREATED)
def criar_chamado(dados: ChamadoEntrada):
    """Recebe JSON, valida com Pydantic e grava no SQLite."""
    with conectar() as conexao:
        cursor = conexao.execute(
            """
            INSERT INTO chamados (aluno, email, assunto, descricao, prioridade)
            VALUES (?, ?, ?, ?, ?)
            """,
            (dados.aluno, dados.email, dados.assunto, dados.descricao, dados.prioridade),
        )
        registro = conexao.execute(
            "SELECT * FROM chamados WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
    return dict(registro)


@app.get("/api/chamados", response_model=list[ChamadoSaida])
def listar_chamados():
    """Consulta os registros persistidos."""
    with conectar() as conexao:
        registros = conexao.execute(
            "SELECT * FROM chamados ORDER BY id DESC"
        ).fetchall()
    return [dict(registro) for registro in registros]


@app.get("/api/chamados/{chamado_id}", response_model=ChamadoSaida)
def consultar_chamado(chamado_id: int):
    with conectar() as conexao:
        registro = conexao.execute(
            "SELECT * FROM chamados WHERE id = ?", (chamado_id,)
        ).fetchone()
    if registro is None:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    return dict(registro)


@app.delete("/api/chamados/{chamado_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_chamado(chamado_id: int):
    """Exclui um chamado pelo ID."""
    with conectar() as conexao:
        cursor = conexao.execute(
            "DELETE FROM chamados WHERE id = ?",
            (chamado_id,),
        )

    if cursor.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail="Chamado não encontrado",
        )