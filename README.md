# Lord of the Rings - Knowledge Graph Frontend

Uma interface web moderna para consultar o grafo de conhecimento do Senhor dos Anéis usando linguagem natural.

## Recursos

- 🎨 **Interface Moderna**: Design temático do Senhor dos Anéis com cores douradas e visual elegante
- 💬 **Chat Interativo**: Interface de conversação para fazer perguntas naturais
- ⚡ **Consultas em Tempo Real**: Conecta com o backend Python + Neo4j + Gemini
- 📊 **Estatísticas do Grafo**: Visualização de dados do banco de conhecimento
- 📱 **Responsivo**: Funciona em desktop, tablet e mobile
- 🔍 **Visualização de Cypher**: Mostra as consultas geradas automaticamente

## Tecnologias

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Backend**: Flask + Python
- **Banco de Dados**: Neo4j
- **LLM**: Google Gemini via Langchain
- **Styling**: CSS customizado com tema Lord of the Rings

## Como Usar

1. **Instalar dependências**:

   ```bash
   pip install -r requirements.txt
   ```

2. **Configurar variáveis de ambiente** (arquivo `.env`):

   ```
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=sua_senha
   GOOGLE_API_KEY=sua_chave_api
   GEMINI_MODEL=gemini-1.5-pro
   MODEL_TEMPERATURE=0.0
   ```

3. **Executar o servidor**:

   ```bash
   python app.py
   ```

4. **Acessar a interface**:
   - Abrir http://localhost:9342 no navegador

## Exemplos de Perguntas

- "List all characters who are Hobbits"
- "Which characters appear in Fellowship of the Ring?"
- "How many Elves are there?"
- "Who are the members of the Fellowship?"
- "What movies are in the database?"

## Estrutura do Frontend

```
frontend/
├── index.html          # Página principal
├── style.css           # Estilos CSS
├── script.js           # Lógica JavaScript
└── README.md           # Esta documentação
```

## APIs Disponíveis

- `GET /api/health` - Status da API
- `GET /api/stats` - Estatísticas do grafo
- `POST /api/query` - Processar pergunta
- `GET /api/examples` - Perguntas de exemplo
- `POST /api/reset` - Reinicializar sistema

## Recursos Especiais

- **Loading Animation**: Animação temática durante processamento
- **Contador de Caracteres**: Limite de 500 caracteres por pergunta
- **Histórico de Mensagens**: Mantém conversação completa
- **Fallback**: Respostas simuladas se API falhar
- **Easter Egg**: Código Konami para efeito especial! 🎮

## Desenvolvimento

Para modificar o frontend:

1. Edite os arquivos em `frontend/`
2. O servidor Flask serve automaticamente os arquivos estáticos
3. Recarregue a página para ver as mudanças

## Troubleshooting

- **Erro de conexão**: Verifique se Neo4j está rodando
- **API não responde**: Verifique as variáveis de ambiente
- **Página não carrega**: Certifique-se que o Flask está rodando na porta 5000
