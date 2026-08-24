FROM continuumio/miniconda3

WORKDIR /app

# environment.yml é copiado antes do restante do código para que o cache de
# camadas do Docker só seja invalidado quando as dependências mudarem.
COPY environment.yml .

RUN conda env create -f environment.yml

COPY app/ ./app/
COPY tests/ ./tests/
COPY pytest.ini README.md ./

# NVIDIA_API_KEY não é definida aqui de propósito: deve ser passada em tempo de
# execução (docker run -e NVIDIA_API_KEY=...) para não ficar gravada na imagem.
CMD ["conda", "run", "--no-capture-output", "-n", "pdf_flashcards", \
     "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
