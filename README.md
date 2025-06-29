# Sistema de Perguntas e Respostas - Senhor dos Anéis

Este projeto implementa um sistema de perguntas e respostas baseado em um grafo de conhecimento do Senhor dos Anéis, utilizando Neo4j e Google Gemini.

## Configuração do Ambiente

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
# Configurações do Neo4j
NEO4J_URI=neo4j+s://seu-database-id.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=sua-senha-neo4j

# Configurações do Google AI
GOOGLE_API_KEY=sua-google-api-key

# Configurações do modelo (opcionais)
GEMINI_MODEL=gemini-1.5-pro
MODEL_TEMPERATURE=0.0
```

**⚠️ IMPORTANTE**: Nunca commite o arquivo `.env` no controle de versão. Ele já está incluído no `.gitignore`.

### 3. Obter Credenciais

#### Neo4j

1. Acesse [Neo4j AuraDB](https://neo4j.com/cloud/aura/)
2. Crie uma instância gratuita
3. Copie a URI, usuário e senha para o arquivo `.env`

#### Google AI

1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crie uma API key
3. Adicione a chave no arquivo `.env`

## Uso

Execute o programa principal:

```bash
python main.py
```

O sistema irá:

1. Conectar ao Neo4j
2. Inicializar o modelo Gemini
3. Aguardar suas perguntas

### Exemplos de Perguntas

- "Quais personagens estão nos filmes do Senhor dos Anéis?"
- "Quantos hobbits existem no Senhor dos Anéis?"
- "Quem é Galadriel?"

Digite `exit` para sair do programa.

## Estrutura do Projeto

```
langchain/
├── main.py           # Código principal refatorado
├── requirements.txt  # Dependências do projeto
├── .env             # Variáveis de ambiente (não versionado)
├── .gitignore       # Arquivos ignorados pelo Git
├── README.md        # Este arquivo
├── test.py          # Testes
├── testai.py        # Testes de AI
└── venv/            # Ambiente virtual (não versionado)
```

## Melhorias Implementadas

- ✅ Variáveis de ambiente para credenciais sensíveis
- ✅ Estrutura modular com funções separadas
- ✅ Tratamento de erros melhorado
- ✅ Mensagens em português
- ✅ `.gitignore` completo
- ✅ Documentação

## Troubleshooting

### Erro de Conexão Neo4j

- Verifique se as credenciais estão corretas no `.env`
- Confirme se a instância Neo4j está ativa

### Erro Google API

- Verifique se a API key está válida
- Confirme se a API do Gemini está habilitada

### Erro de Dependências

- Execute `pip install -r requirements.txt`
- Verifique se está usando o ambiente virtual correto
