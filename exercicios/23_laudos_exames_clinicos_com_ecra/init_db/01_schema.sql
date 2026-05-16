-- Dados fictícios para formação (LangChain / RAG). Não usar em decisões clínicas reais.
SET client_encoding = 'UTF8';

CREATE TABLE pacientes (
    id SERIAL PRIMARY KEY,
    nome_completo TEXT NOT NULL,
    idade INTEGER NOT NULL CHECK (idade >= 0 AND idade <= 120),
    sexo CHAR(1) CHECK (sexo IN ('M', 'F', 'X')),
    alergias TEXT,
    observacoes_clinicas TEXT
);

CREATE TABLE exames_laboratoriais (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes (id) ON DELETE CASCADE,
    codigo TEXT NOT NULL,
    data_exame DATE NOT NULL,
    painel TEXT,
    laudo_texto TEXT NOT NULL,
    valores_estruturados JSONB
);

CREATE TABLE avaliacoes_engine (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes (id) ON DELETE CASCADE,
    nivel_gravidade TEXT NOT NULL,
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
    payload_json JSONB NOT NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_exames_paciente ON exames_laboratoriais (paciente_id);
CREATE INDEX idx_avaliacoes_paciente ON avaliacoes_engine (paciente_id, criado_em DESC);

INSERT INTO pacientes (nome_completo, idade, sexo, alergias, observacoes_clinicas) VALUES
('Ana Beatriz Ferreira', 34, 'F', 'Penicilina', 'Gestante 24ª semana; sem queixas agudas.'),
('Bruno Miguel Costa', 52, 'M', 'Nega', 'Hipertenso em seguimento; tabagista 20 anos-maço.'),
('Carla Sofia Ribeiro', 67, 'F', 'AAS', 'DM2 e DRC estádio 3; hipotireoidismo.'),
('Daniel Filipe Araújo', 19, 'M', 'Nega', 'Atleta universitário; desmaio recente em treino.'),
('Eduarda Matos Lopes', 41, 'F', 'Látex', 'Dor torácica atípica há 10 dias; ansiedade documentada.'),
('Francisco Henrique Dias', 58, 'M', 'Nega', 'Obesidade grau II; dislipidemia.'),
('Graça Isabel Neves', 73, 'F', 'Sulfonamidas', 'ICC classe II; fibrilação auricular anticoagulada.'),
('Hugo Alexandre Teixeira', 45, 'M', 'Nega', 'Cefaleia progressiva; exame neurológico normal no SU.'),
('Inês Patrícia Moura', 29, 'F', 'Nega', 'Síndrome gripal há 5 dias; sat O2 ambiente 97%.'),
('João Pedro Sequeira', 61, 'M', 'Iodocontrastados', 'Angina estável; coronariografia programada.');

INSERT INTO exames_laboratoriais (paciente_id, codigo, data_exame, painel, laudo_texto, valores_estruturados) VALUES
(1, 'HEM-2026-001', '2026-05-01', 'Hemograma',
 'Hemograma com série vermelha e branca dentro dos parâmetros de referência. Plaquetas adequadas. Sem morfologia sugestiva de deficiência ferro.',
 '{"hb": 12.8, "ht": 38.2, "leucocitos": 7800, "plaquetas": 210000}'::jsonb),
(1, 'BIO-2026-002', '2026-05-01', 'Bioquímica',
 'Função renal e hepática sem alterações relevantes. Glicemia jejum 88 mg/dL. Perfil lipídico aceitável para contexto gestacional.',
 '{"creatinina": 0.7, "tgo": 22, "tgp": 28, "glicemia": 88}'::jsonb),

(2, 'HEM-2026-010', '2026-05-02', 'Hemograma',
 'Leucocitose discreta (14.200/µL) com desvio esquerdo leve. Hemoglobina 15.1 g/dL. Sugere reavaliação clínica infecciosa/inflamatória.',
 '{"hb": 15.1, "leucocitos": 14200}'::jsonb),
(2, 'BIO-2026-011', '2026-05-02', 'Rim e eletrólitos',
 'Creatinina limítrofe alta-normal (1.35 mg/dL) com eGFR estimado limítrofe para idade. Potássio 4.2 mEq/L.',
 '{"creatinina": 1.35, "k": 4.2}'::jsonb),

(3, 'BIO-2026-020', '2026-05-03', 'Função renal',
 'Creatinina 2.10 mg/dL; eGFR reduzido compatível com DRC estádio 3b. Ureia elevada. Albumina urinária não incluída neste painel — correlacionar com nefrologia.',
 '{"creatinina": 2.1, "ureia": 78}'::jsonb),
(3, 'HEM-2026-021', '2026-05-03', 'Hemograma',
 'Anemia normocítica normocrómica (Hb 10.2 g/dL). Plaquetas normais. Solicitada avaliação etiológica em contexto de nefropatia.',
 '{"hb": 10.2}'::jsonb),

(4, 'CARD-2026-030', '2026-05-04', 'Marcadores cardíacos',
 'Troponina I ultrassensível elevada em curva ascendente (valor inicial 45 ng/L, repetido 120 ng/L às 3h). CK-MB limítrofe. Correlação clínica urgente com síndrome coronariana aguda.',
 '{"troponina_i": 120, "ck_mb": 5.2}'::jsonb),
(4, 'ECG-REF', '2026-05-04', 'Nota laboratorial',
 'ECG não laboratorial — referenciar urgência se dor torácica ou equivalente persistir.', '{}'::jsonb),

(5, 'BIO-2026-040', '2026-05-05', 'Tireoide',
 'TSH suprimido (0.10 µUI/mL) com T4 livre limite alto. Sugere hipertireoidismo subclínico/overt — correlacionar clinicamente.',
 '{"tsh": 0.1, "t4livre": 1.8}'::jsonb),

(6, 'BIO-2026-050', '2026-05-06', 'Perfil metabólico',
 'Glicemia 142 mg/dL em jejum relativo; HbA1c 6.2%. Colesterol LDL 165 mg/dL; triglicerídeos 220 mg/dL. AST/ALT normais.',
 '{"glicemia": 142, "hba1c": 6.2, "ldl": 165, "tg": 220}'::jsonb),

(7, 'BIO-2026-060', '2026-05-07', 'Eletrólitos e rim',
 'Hipercalemia moderada (K 5.8 mEq/L). Creatinina 1.55 mg/dL. Sugere monitorização cardiológica e revisão de fármacos/função renal.',
 '{"k": 5.8, "creatinina": 1.55}'::jsonb),

(8, 'BIO-2026-070', '2026-05-08', 'Hemograma e PCR',
 'Hemograma sem citopenias. PCR 4 mg/L (baixa). Sem achados laboratoriais agudos neste painel.',
 '{"pcr": 4}'::jsonb),

(9, 'HEM-2026-080', '2026-05-09', 'Hemograma',
 'Leucopenia leve (3.800/µL) com linfopenia relativa. Hemoglobina normal. Vigilância viral a considerar em contexto clínico.',
 '{"leucocitos": 3800}'::jsonb),

(10, 'BIO-2026-090', '2026-05-10', 'Pré-operatório',
 'Hemograma e coagulação dentro da referência. Creatinina 1.0 mg/dL. ECG não laboratorial — avaliação cardiológica em curso.',
 '{"creatinina": 1.0}'::jsonb);
