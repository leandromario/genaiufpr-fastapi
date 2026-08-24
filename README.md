# PDF Flashcards

API em FastAPI que recebe um arquivo PDF e gera, a partir do seu conteúdo, um **resumo em tópicos** ou um conjunto de **flashcards de estudo** (pergunta/resposta).

O texto é extraído localmente com `pypdf` e enviado a um modelo de linguagem hospedado no catálogo [NVIDIA NIM](https://build.nvidia.com/models), que oferece créditos de inferência gratuitos e uma API compatível com o formato da OpenAI.


Projeto final da disciplina Python da Especialização em GenAI/UFPR, lecionado por prof. Paulo Lisboa de Almeida e prof. André Ricardo Abed Grégio.

## Endpoints

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Confirma que o serviço está no ar e informa o modelo configurado |
| `POST` | `/pdf/resumo` | Recebe um PDF e devolve `{"resumo": "..."}` |
| `POST` | `/pdf/flashcards` | Recebe um PDF e devolve `{"flashcards": [{"pergunta": "...", "resposta": "..."}]}` |

Os dois endpoints de PDF recebem o arquivo como `multipart/form-data` no campo `arquivo`.

`GET /` existe para tornar a verificação de um deploy trivial - basta abrir o endereço do servidor no navegador:

```json
{"servico":"PDF Flashcards","status":"ok","modelo":"meta/llama-3.1-8b-instruct","documentacao":"/docs"}
```

A documentação interativa (Swagger UI), que permite testar o upload direto pelo navegador, fica em `/docs`.

## Pré-requisitos

Uma chave de API gratuita da NVIDIA:

1. Crie uma conta em [build.nvidia.com](https://build.nvidia.com/models) (NVIDIA Developer Program, sem cartão de crédito).
2. Escolha um modelo e gere sua API key.
3. Exporte a chave no ambiente:

```bash
export NVIDIA_API_KEY=nvapi-...
```

## Executando com Docker

```bash
docker build -t pdf-flashcards .
```

```bash
docker run -p 8000:8000 -e NVIDIA_API_KEY=$NVIDIA_API_KEY pdf-flashcards
```

A API sobe em `http://localhost:8000`. Teste com:

```bash
curl -X POST http://localhost:8000/pdf/resumo -F "arquivo=@caminho/para/arquivo.pdf"
```

## Executando localmente com conda

```bash
conda env create -f environment.yml
```

```bash
conda activate pdf_flashcards && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Estrutura

```
app/
├── config.py        Configuração lida do ambiente (pydantic-settings)
├── modelos.py       Flashcard e schemas de resposta
├── excecoes.py      Hierarquia de erros de domínio, com o status HTTP que cada um representa
├── extracao.py      ExtratorPDF - lê bytes, valida limites, devolve texto
├── gerador.py       GeradorDeTexto - interface abstrata do provedor de LLM
├── gerador_nim.py   GeradorNIM - implementação sobre o NVIDIA NIM
├── prompts.py       Construção dos prompts
├── rotas.py         Endpoints, recebendo extrator e gerador por injeção de dependência
└── main.py          Monta a aplicação e traduz erros de domínio em respostas HTTP
```

As camadas de extração e geração não conhecem HTTP: levantam exceções de domínio, traduzidas em `main.py`. As rotas dependem da abstração `GeradorDeTexto`, de modo que trocar de provedor de modelo é escrever uma nova subclasse, sem tocar nos endpoints.

## Testes

A suíte roda inteiramente offline, sem rede e sem chave de API porque o gerador real é substituído por um dublê via `dependency_overrides`:

```bash
docker run --rm pdf-flashcards conda run --no-capture-output -n pdf_flashcards python -m pytest -q
```

Com o ambiente conda ativado localmente, basta `pytest`.

## Configuração

Variáveis de ambiente reconhecidas:

| Variável | Padrão | Descrição |
|---|---|---|
| `NVIDIA_API_KEY` | - | **Obrigatória.** Chave de API do NVIDIA NIM. |
| `NIM_BASE_URL` | `https://integrate.api.nvidia.com/v1` | Endpoint de inferência. |
| `NIM_MODEL` | `meta/llama-3.1-8b-instruct` | Modelo do catálogo NIM a ser usado. |
| `MAX_PAGINAS` | `30` | Limite de páginas do PDF enviado. |
| `MAX_MB` | `10` | Limite de tamanho do PDF enviado, em MB. |

Sem `NVIDIA_API_KEY` a aplicação não sobe: a configuração é validada na inicialização, para que um container mal configurado falhe de imediato em vez de só na primeira requisição.

A chave nunca é gravada na imagem Docker, ela é lida do ambiente em tempo de execução.

## Respostas de erro

| Status | Situação |
|---|---|
| `413` | PDF excede o limite de páginas ou de tamanho |
| `422` | Arquivo não é um PDF válido, ou não possui texto extraível (ex.: digitalizado) |
| `502` | Falha ao consultar o modelo, ou resposta fora do formato esperado |

## Licença

Projeto acadêmico, disponibilizado como portfólio.
