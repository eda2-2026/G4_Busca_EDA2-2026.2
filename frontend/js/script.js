const formBusca = document.getElementById("form-busca");
const inputTermo = document.getElementById("input-termo");
const mensagemEstado = document.getElementById("mensagem-estado");

const painelInfo = document.getElementById("painel-info");
const infoAlgoritmo = document.getElementById("info-algoritmo");
const infoComparacoes = document.getElementById("info-comparacoes");
const infoTempo = document.getElementById("info-tempo");
const infoTotal = document.getElementById("info-total");

const painelComparacao = document.getElementById("painel-comparacao");
const comparacaoNota = document.getElementById("comparacao-nota");

const listaResultados = document.getElementById("lista-resultados");
const resultadosContagem = document.getElementById("resultados-contagem");

const botaoExperimento = document.getElementById("botao-experimento");
const tabelaExperimentos = document.getElementById("tabela-experimentos");
const tabelaExperimentosCorpo = document.getElementById("tabela-experimentos-corpo");
const experimentosMensagem = document.getElementById("experimentos-mensagem");

const NOMES_ALGORITMO = {
  sequencial: "Busca Sequencial",
  binaria: "Busca Binária",
};

function formatarTempo(segundos) {
  if (segundos < 0.000001) {
    return `${(segundos * 1_000_000_000).toFixed(0)} ns`;
  }
  if (segundos < 0.001) {
    return `${(segundos * 1_000_000).toFixed(1)} µs`;
  }
  if (segundos < 1) {
    return `${(segundos * 1000).toFixed(3)} ms`;
  }
  return `${segundos.toFixed(4)} s`;
}

function formatarNumero(numero) {
  return numero.toLocaleString("pt-BR");
}

function exibirMensagem(elemento, texto, tipo = "normal") {
  elemento.textContent = texto;
  elemento.hidden = !texto;
  elemento.classList.toggle("mensagem-estado--erro", tipo === "erro");
}

function renderizarVagas(vagas) {
  listaResultados.innerHTML = "";

  if (!vagas || vagas.length === 0) {
    listaResultados.innerHTML =
      '<p class="estado-vazio">Nenhuma vaga encontrada para esse termo.</p>';
    resultadosContagem.textContent = "";
    return;
  }

  resultadosContagem.textContent =
    vagas.length === 1 ? "1 vaga" : `${vagas.length} vagas`;

  const fragmento = document.createDocumentFragment();

  for (const vaga of vagas) {
    const card = document.createElement("article");
    card.className = "card-vaga";

    const descricaoCurta =
      (vaga.descricao || "").length > 220
        ? vaga.descricao.slice(0, 220).trim() + "…"
        : vaga.descricao || "Sem descrição disponível.";

    card.innerHTML = `
      <h3 class="card-vaga__titulo">${escapeHtml(vaga.titulo || "Sem título")}</h3>
      <div class="card-vaga__meta">
        <span>Empresa: ${escapeHtml(vaga.empresa || "Não informado")}</span>
        <span>Localização: ${escapeHtml(vaga.localizacao || "Não informado")}</span>
      </div>
      <p class="card-vaga__descricao">${escapeHtml(descricaoCurta)}</p>
      ${
        vaga.url
          ? `<a class="card-vaga__link" href="${escapeAttr(vaga.url)}" target="_blank" rel="noopener">Ver vaga →</a>`
          : ""
      }
    `;

    fragmento.appendChild(card);
  }

  listaResultados.appendChild(fragmento);
}

function escapeHtml(texto) {
  const div = document.createElement("div");
  div.textContent = texto;
  return div.innerHTML;
}

function escapeAttr(texto) {
  return String(texto).replace(/"/g, "&quot;");
}

async function executarBuscaUnica(termo, algoritmo) {
  const resposta = await fetch(
    `/api/buscar?termo=${encodeURIComponent(termo)}&algoritmo=${algoritmo}`
  );
  const dados = await resposta.json();

  if (!resposta.ok) {
    throw new Error(dados.erro || "Erro ao realizar a busca.");
  }

  painelComparacao.hidden = true;
  painelInfo.hidden = false;

  infoAlgoritmo.textContent = NOMES_ALGORITMO[algoritmo] || algoritmo;
  infoComparacoes.textContent = formatarNumero(dados.comparacoes);
  infoTempo.textContent = formatarTempo(dados.tempo_execucao_segundos);
  infoTotal.textContent = formatarNumero(dados.total_encontrado);

  renderizarVagas(dados.vagas);
}

async function executarComparacao(termo) {
  const resposta = await fetch(`/api/comparar?termo=${encodeURIComponent(termo)}`);
  const dados = await resposta.json();

  if (!resposta.ok) {
    throw new Error(dados.erro || "Erro ao comparar os algoritmos.");
  }

  painelInfo.hidden = true;
  painelComparacao.hidden = false;

  const { sequencial, binaria } = dados;
  const maiorComparacao = Math.max(sequencial.comparacoes, binaria.comparacoes, 1);

  atualizarCorrida("seq", sequencial, maiorComparacao);
  atualizarCorrida("bin", binaria, maiorComparacao);

  const diferenca =
    sequencial.comparacoes > 0 && binaria.comparacoes > 0
      ? (sequencial.comparacoes / binaria.comparacoes).toFixed(1)
      : null;

  comparacaoNota.textContent = diferenca
    ? `Nesta busca, a Busca Sequencial realizou ${diferenca}× mais comparações que a Busca Binária, em uma base com ${formatarNumero(dados.total_vagas_na_base)} vagas.`
    : `Base com ${formatarNumero(dados.total_vagas_na_base)} vagas.`;

  const respostaLista = await fetch(
    `/api/buscar?termo=${encodeURIComponent(termo)}&algoritmo=binaria`
  );
  const dadosLista = await respostaLista.json();
  renderizarVagas(dadosLista.vagas);
}

function atualizarCorrida(prefixo, resultado, maiorComparacao) {
  const numero = document.getElementById(`corrida-${prefixo}-numero`);
  const barra = document.getElementById(`corrida-${prefixo}-barra`);
  const tempo = document.getElementById(`corrida-${prefixo}-tempo`);
  const encontrado = document.getElementById(`corrida-${prefixo}-resultado`);

  numero.textContent = formatarNumero(resultado.comparacoes);
  tempo.textContent = formatarTempo(resultado.tempo_execucao_segundos);
  encontrado.textContent = resultado.encontrado
    ? "vaga encontrada"
    : "vaga não encontrada";

  const proporcao = Math.max((resultado.comparacoes / maiorComparacao) * 100, 4);

  barra.style.width = "0%";
  requestAnimationFrame(() => {
    barra.style.width = `${proporcao}%`;
  });
}

formBusca.addEventListener("submit", async (evento) => {
  evento.preventDefault();

  const termo = inputTermo.value.trim();
  const algoritmoSelecionado = formBusca.elements["algoritmo"].value;

  if (!termo) {
    exibirMensagem(mensagemEstado, "Digite um cargo ou título de vaga para buscar.", "erro");
    return;
  }

  exibirMensagem(mensagemEstado, "Buscando...");

  try {
    if (algoritmoSelecionado === "comparar") {
      await executarComparacao(termo);
    } else {
      await executarBuscaUnica(termo, algoritmoSelecionado);
    }
    exibirMensagem(mensagemEstado, "");
  } catch (erro) {
    exibirMensagem(mensagemEstado, erro.message, "erro");
  }
});

botaoExperimento.addEventListener("click", async () => {
  botaoExperimento.disabled = true;
  botaoExperimento.textContent = "Executando...";
  exibirMensagem(experimentosMensagem, "");

  try {
    const resposta = await fetch("/api/experimentos");
    const dados = await resposta.json();

    if (!resposta.ok) {
      throw new Error(
        dados.erro ||
          "Não foi possível executar o experimento. Gere as massas de teste primeiro."
      );
    }

    renderizarTabelaExperimentos(dados.resultados);
  } catch (erro) {
    exibirMensagem(experimentosMensagem, erro.message, "erro");
    tabelaExperimentos.hidden = true;
  } finally {
    botaoExperimento.disabled = false;
    botaoExperimento.textContent = "Rodar experimento";
  }
});

function renderizarTabelaExperimentos(resultados) {
  tabelaExperimentosCorpo.innerHTML = "";

  for (const linha of resultados) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${formatarNumero(linha.tamanho)}</td>
      <td class="celula-sequencial">${formatarNumero(linha.sequencial.comparacoes)}</td>
      <td class="celula-binaria">${formatarNumero(linha.binaria.comparacoes)}</td>
      <td class="celula-sequencial">${formatarTempo(linha.sequencial.tempo_execucao_segundos)}</td>
      <td class="celula-binaria">${formatarTempo(linha.binaria.tempo_execucao_segundos)}</td>
    `;
    tabelaExperimentosCorpo.appendChild(tr);
  }

  tabelaExperimentos.hidden = false;
}

(async function carregarVagasIniciais() {
  try {
    const resposta = await fetch("/api/vagas");
    const dados = await resposta.json();
    renderizarVagas((dados.vagas || []).slice(0, 6));
    if (dados.vagas && dados.vagas.length > 0) {
      resultadosContagem.textContent = `mostrando 6 de ${formatarNumero(dados.total)}`;
    }
  } catch (erro) {
    console.warn("Não foi possível carregar as vagas iniciais.", erro);
  }
})();
