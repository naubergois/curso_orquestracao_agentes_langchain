-- Processos fictícios (pedagógico) + vínculo a PDFs em `pdf_fontes/` (nome do ficheiro = metadata Chroma).
SET client_encoding = 'UTF8';

CREATE TABLE IF NOT EXISTS processos (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(96) NOT NULL UNIQUE,
    tribunal VARCHAR(256) NOT NULL,
    tipo_acao VARCHAR(160),
    estado VARCHAR(80),
    data_distribuicao DATE,
    partes TEXT NOT NULL,
    objeto TEXT NOT NULL,
    sumario_factual TEXT,
    valor_causa NUMERIC(15, 2),
    temas TEXT,
    criado_em TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS processo_anexos_pdf (
    processo_id INTEGER NOT NULL REFERENCES processos (id) ON DELETE CASCADE,
    nome_ficheiro VARCHAR(256) NOT NULL,
    descricao TEXT,
    PRIMARY KEY (processo_id, nome_ficheiro)
);
