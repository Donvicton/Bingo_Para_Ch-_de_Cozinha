# 🏠 Bingo · Chá de Casa Nova

App em Streamlit para conduzir o bingo do Chá de Casa Nova de **Raelle e Donivcton**. Ele sorteia as palavras e avisa na hora qual cartela ganhou.

O app usa as **50 cartelas impressas** do evento. Cada uma tem uma grade 5×5 com 24 utensílios de casa e o espaço **LIVRE** no centro. As palavras vêm de uma lista de 50 itens.

## Funcionalidades

- **Sorteio sem repetição**: cada palavra aparece em destaque, com a rodada e o número da lista (ex.: *Rodada 7 · Nº 21 · Xícara*).
- **Detecção automática de vencedoras**: mostra o número da(s) cartela(s) que completaram e em qual rodada, com balões na tela.
- **Dois modos de vitória**:
  - *Cartela cheia*: todas as 24 palavras marcadas.
  - *Linha, coluna ou diagonal*: qualquer uma das 12 linhas possíveis completa.
- **Roleta de desempate**: quando duas ou mais cartelas completam na mesma rodada, aparece o botão **🎡 Girar roleta**. A roleta gira com som de tique e para na cartela vencedora, sorteada de forma aleatória.
- **"Falta 1"**: lista as cartelas a uma palavra de ganhar.
- **Conferir cartela**: digite o número e veja a grade com as palavras já sorteadas destacadas. Serve para validar quem gritou bingo.
- **Marcação manual**: para quando o sorteio é feito em papel e o app serve só para conferir.
- **Desfazer** a última palavra e **zerar** o jogo.
- **Ordem do sorteio** completa, para consulta.

## Estrutura

```
.
├── app.py            # Interface e lógica do sorteio
├── cartelas.json     # As 50 cartelas (grade 5×5 cada), extraídas do PDF impresso
└── requirements.txt  # Dependências
```

`cartelas.json` é um objeto em que a chave é o número da cartela e o valor é a grade (lista de 5 linhas com 5 palavras):

```json
{
  "1": [
    ["Forma de bolo", "Saboneteira", "Guardanapo", "Peneira", "Porta papel toalha"],
    ["Prato", "Assadeira", "Faca", "Colher de pau", "Escumadeira"],
    ["Vassoura", "Jarra", "LIVRE", "Frigideira", "Abridor de lata"],
    ...
  ]
}
```

## Como rodar localmente

Requer Python 3.9+.

```bash
pip install -r requirements.txt
streamlit run app.py
```

O app abre em `http://localhost:8501`.

## Deploy no Streamlit Community Cloud

1. Suba `app.py`, `cartelas.json` e `requirements.txt` na raiz de um repositório no GitHub.
2. Entre em [share.streamlit.io](https://share.streamlit.io) com a conta do GitHub.
3. Clique em **Create app**, escolha o repositório, a branch `main` e o arquivo `app.py`.
4. Defina a URL do app e clique em **Deploy**.

No Android, abra a URL no Chrome e use **⋮ → Adicionar à tela inicial** para ter um atalho com cara de app.

## Observações

- **O estado do sorteio fica na sessão do navegador.** Se a página for recarregada, o jogo zera. Durante o evento, evite atualizar a página.
- **Apps gratuitos do Streamlit Cloud hibernam** após um período sem acesso. Abra o link um pouco antes do evento para acordá-lo.
- As palavras são comparadas de forma exata, então *Organizador* e *Cesto organizador* são itens diferentes, como nas cartelas.

## Como funciona a verificação

Para cada cartela, o app conta quantas palavras ainda faltam:

- **Cartela cheia**: número de células não marcadas, onde LIVRE conta como marcada.
- **Linha/coluna/diagonal**: o menor número de faltantes entre as 12 linhas possíveis (5 horizontais, 5 verticais e 2 diagonais).

A cartela ganha quando esse número chega a zero. A rodada da vitória é calculada reprocessando a ordem do sorteio palavra por palavra.
