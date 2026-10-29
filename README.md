# Qualidade do Ar — MongoDB + Redis com Python

Bancos de Dados e Novas Tecnologias — Unochapecó (Profa. Me. Monica Tissiani De Toni Pereira)

## Integrantes
- Gabriel Gerhard
- João Marcelo Lemes
- Juan Facenda

## Estrutura
- `codigo/` — scripts de banco (JS) e programas Python
- `documentacao/` — relatório técnico (com diagrama de arquitetura) e roteiro da apresentação

## Como executar
```bash
pip install -r requirements.txt
# MongoDB em localhost:27017 e Redis em localhost:6379
python codigo/popular.py          # cadastra 6 sensores / 3 cidades e gera 1.728 medições
python codigo/agregacao.py        # resumos horários -> Redis
python codigo/consultas.py        # consulta por sensor/intervalo e exibe Hashes
python codigo/testes/teste_dados_novos.py   # testes com dados diferentes
```
