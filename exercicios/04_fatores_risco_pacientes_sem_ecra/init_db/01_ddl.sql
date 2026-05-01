-- Dados de demonstração (curso). Não são orientação clínica.

CREATE TABLE pacientes (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    idade INT NOT NULL CHECK (idade >= 0 AND idade <= 120),
    sexo VARCHAR(20) NOT NULL,
    imc NUMERIC(4, 1) NOT NULL CHECK (imc > 0 AND imc < 100),
    pressao_sistolica INT NOT NULL CHECK (pressao_sistolica > 0),
    pressao_diastolica INT NOT NULL CHECK (pressao_diastolica > 0),
    glicemia_jejum INT NOT NULL,
    colesterol_ldl INT NOT NULL,
    hdl INT NOT NULL,
    triglicerideos INT NOT NULL,
    tabagismo VARCHAR(30) NOT NULL,
    atividade_fisica VARCHAR(30) NOT NULL,
    historico_familiar_cv BOOLEAN NOT NULL,
    notas_clinicas TEXT
);
