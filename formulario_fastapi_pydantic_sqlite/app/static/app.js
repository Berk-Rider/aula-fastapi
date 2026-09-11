const formulario = document.querySelector("#formulario");
const saida = document.querySelector("#saida");
const statusResposta = document.querySelector("#status");
const lista = document.querySelector("#lista");

function mostrarResposta(codigo, dados, sucesso) {
  statusResposta.textContent = `HTTP ${codigo}`;
  statusResposta.className = sucesso ? "sucesso" : "erro";
  saida.textContent = JSON.stringify(dados, null, 2);
}

function escapar(texto) {
  const elemento = document.createElement("div");
  elemento.textContent = texto;
  return elemento.innerHTML;
}

formulario.addEventListener("submit", async (evento) => {
  evento.preventDefault();

  // O navegador apenas coleta e envia os valores. A validação do contrato
  // acontece no servidor, dentro do modelo Pydantic ChamadoEntrada.
  const dados = Object.fromEntries(new FormData(formulario));

  try {
    const resposta = await fetch("/api/chamados", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados)
    });

    const conteudo = await resposta.json();
    mostrarResposta(resposta.status, conteudo, resposta.ok);

    if (resposta.ok) {
      formulario.reset();
      await consultarPersistencia();
    }
  } catch (erro) {
    mostrarResposta("sem conexão", { erro: erro.message }, false);
  }
});

async function consultarPersistencia() {
  try {
    const resposta = await fetch("/api/chamados");
    const chamados = await resposta.json();

    if (chamados.length === 0) {
      lista.innerHTML = '<p class="vazio">O banco ainda não possui registros.</p>';
      return;
    }

    lista.innerHTML = chamados.map(chamado => `
      <article class="item">
        <strong>#${chamado.id} — ${escapar(chamado.assunto)}</strong>
        <div>${escapar(chamado.aluno)} · ${escapar(chamado.email)}</div>
        <div>Prioridade: ${escapar(chamado.prioridade)}</div>
      </article>
    `).join("");
  } catch (erro) {
    lista.innerHTML = '<p class="vazio">Não foi possível consultar os dados.</p>';
  }
}

document.querySelector("#consultar").addEventListener("click", consultarPersistencia);
consultarPersistencia();

