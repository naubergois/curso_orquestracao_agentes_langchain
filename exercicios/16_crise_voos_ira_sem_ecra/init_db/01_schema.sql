-- Exercício 16 — simulação educativa: voos internacionais fictícios e cenário de crise operacional.
-- Dados e eventos são **fictícios** (demonstração do curso).

CREATE TABLE aeroportos (
    id SERIAL PRIMARY KEY,
    cod_iata CHAR(3) NOT NULL UNIQUE,
    nome VARCHAR(120) NOT NULL,
    pais VARCHAR(80) NOT NULL,
    notas_seguranca TEXT
);

CREATE TABLE voos (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(16) NOT NULL,
    companhia VARCHAR(40) NOT NULL DEFAULT 'DemoAir',
    origem_iata CHAR(3) NOT NULL REFERENCES aeroportos (cod_iata),
    destino_iata CHAR(3) NOT NULL REFERENCES aeroportos (cod_iata),
    partida_prevista TIMESTAMPTZ NOT NULL,
    estado VARCHAR(24) NOT NULL DEFAULT 'programado',
    motivo_cancelamento TEXT,
    lugares_disponiveis INT NOT NULL DEFAULT 0 CHECK (lugares_disponiveis >= 0),
    CONSTRAINT ck_voos_estado CHECK (
        estado IN ('programado', 'em_checkin', 'cancelado', 'concluido')
    )
);

CREATE INDEX idx_voos_partida ON voos (partida_prevista);
CREATE INDEX idx_voos_estado ON voos (estado);

CREATE TABLE reservas (
    id SERIAL PRIMARY KEY,
    pnr VARCHAR(10) NOT NULL UNIQUE,
    nome_passageiro VARCHAR(120) NOT NULL,
    voo_id INT NOT NULL REFERENCES voos (id),
    estado VARCHAR(24) NOT NULL DEFAULT 'confirmada',
    novo_voo_id INT REFERENCES voos (id),
    CONSTRAINT ck_res_estado CHECK (
        estado IN ('confirmada', 'remarcada', 'reembolso_solicitado', 'anulada')
    )
);

CREATE TABLE campanhas_comunicacao (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    corpo TEXT NOT NULL,
    publico_alvo VARCHAR(120),
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE avaliacoes_risco (
    id SERIAL PRIMARY KEY,
    tipo VARCHAR(80) NOT NULL,
    descricao TEXT NOT NULL,
    severidade SMALLINT NOT NULL CHECK (severidade BETWEEN 1 AND 5),
    recomendacao TEXT NOT NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO aeroportos (cod_iata, nome, pais, notas_seguranca) VALUES
    ('IKA', 'Aeroporto Imam Khomeini (fictício curso)', 'Irão', 'Cenário simulado: instabilidade regional — espaço aéreo restrito (dados fictícios).'),
    ('DXB', 'Dubai International', 'EAU', NULL),
    ('IST', 'Istanbul Airport', 'Turquia', NULL),
    ('LHR', 'London Heathrow', 'Reino Unido', NULL),
    ('CDG', 'Paris Charles de Gaulle', 'França', NULL),
    ('DOH', 'Hamad International', 'Catar', NULL);

-- Voos cancelados (ligação ou destino IKA — simulação de crise)
INSERT INTO voos (numero, origem_iata, destino_iata, partida_prevista, estado, motivo_cancelamento, lugares_disponiveis)
VALUES
    ('DA401', 'IKA', 'LHR', NOW() + INTERVAL '36 hours', 'cancelado',
     'Simulação: restrição de espaço aéreo na região — operações suspensas (cenário educativo).', 0),
    ('DA402', 'DXB', 'IKA', NOW() + INTERVAL '40 hours', 'cancelado',
     'Simulação: destino indisponível por decisão operacional conjunta (fictício).', 0),
    ('DA403', 'IST', 'IKA', NOW() + INTERVAL '48 hours', 'cancelado',
     'Simulação: desvio de rotas internacionais; chegada a IKA adiada indefinidamente (fictício).', 0),
    ('DA404', 'IKA', 'CDG', NOW() + INTERVAL '52 hours', 'cancelado',
     'Simulação: mesmo motivo operacional que DA401 (fictício).', 0);

-- Alternativas operacionais (mesmos destinos finais úteis para remarcação)
INSERT INTO voos (numero, origem_iata, destino_iata, partida_prevista, estado, motivo_cancelamento, lugares_disponiveis)
VALUES
    ('DA551', 'IST', 'LHR', NOW() + INTERVAL '38 hours', 'programado', NULL, 42),
    ('DA552', 'DXB', 'LHR', NOW() + INTERVAL '42 hours', 'programado', NULL, 30),
    ('DA553', 'DOH', 'CDG', NOW() + INTERVAL '44 hours', 'programado', NULL, 55),
    ('DA554', 'IST', 'CDG', NOW() + INTERVAL '50 hours', 'programado', NULL, 60);

-- Passageiros em voos cancelados
INSERT INTO reservas (pnr, nome_passageiro, voo_id, estado)
SELECT 'PNR01A', 'Maria Silva', id, 'confirmada' FROM voos WHERE numero = 'DA401';

INSERT INTO reservas (pnr, nome_passageiro, voo_id, estado)
SELECT 'PNR02B', 'João Costa', id, 'confirmada' FROM voos WHERE numero = 'DA402';

INSERT INTO reservas (pnr, nome_passageiro, voo_id, estado)
SELECT 'PNR03C', 'Ana Rodrigues', id, 'confirmada' FROM voos WHERE numero = 'DA404';
