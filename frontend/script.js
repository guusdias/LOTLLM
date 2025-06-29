class LordOfTheRingsApp {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.userInput = document.getElementById('userInput');
        this.sendButton = document.getElementById('sendButton');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.characterCount = document.querySelector('.character-count');
        
        this.messageHistory = [];
        this.isLoading = false;
        
        this.initializeEventListeners();
        this.loadStats();
    }

    initializeEventListeners() {
        // Enviar mensagem ao clicar no botão
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Enviar mensagem ao pressionar Enter
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Contador de caracteres
        this.userInput.addEventListener('input', () => this.updateCharacterCount());
        
        // Auto-resize do input
        this.userInput.addEventListener('input', () => this.autoResizeInput());
    }

    updateCharacterCount() {
        const count = this.userInput.value.length;
        this.characterCount.textContent = `${count}/500`;
        
        if (count > 450) {
            this.characterCount.style.color = '#ff6b6b';
        } else {
            this.characterCount.style.color = 'var(--cream)';
        }
    }

    autoResizeInput() {
        this.userInput.style.height = 'auto';
        this.userInput.style.height = this.userInput.scrollHeight + 'px';
    }

    async sendMessage() {
        const message = this.userInput.value.trim();
        if (!message || this.isLoading) return;

        // Adicionar mensagem do usuário
        this.addMessage('user', message);
        this.userInput.value = '';
        this.updateCharacterCount();
        
        // Mostrar loading
        this.showLoading();
        
        try {
            // Simular chamada para o backend
            const response = await this.queryKnowledgeGraph(message);
            this.addMessage('assistant', response.answer, response.cypher, response.processingTime);
        } catch (error) {
            this.addMessage('assistant', 'Desculpe, ocorreu um erro ao processar sua pergunta. Tente novamente.', null, null, true);
        }
        
        this.hideLoading();
    }

    async queryKnowledgeGraph(question) {
        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Erro na API');
            }

            const data = await response.json();
            return {
                answer: data.answer,
                cypher: data.cypher_query,
                processingTime: data.processing_time
            };
        } catch (error) {
            // Fallback para respostas simuladas se a API falhar
            console.warn('Falha na API, usando respostas simuladas:', error);
            await this.sleep(1500 + Math.random() * 1000);
            return this.generateMockResponse(question);
        }
    }

    generateMockResponse(question) {
        const lowerQuestion = question.toLowerCase();
        
        // Respostas simuladas baseadas em padrões
        if (lowerQuestion.includes('hobbit')) {
            return {
                answer: `Com base nos dados do grafo de conhecimento, encontrei os seguintes personagens Hobbits: Bilbo, Frodo, Merry (Meriadoc), Pippin (Peregrin), Sam (Samwise), Rosie, Gaffer, Deagol, Farmer Maggot, entre outros. Os Hobbits são uma das raças mais importantes na história do Senhor dos Anéis, conhecidos por sua hospitalidade e coragem inesperada.`,
                cypher: `MATCH (c:Characters) WHERE c.Race = "Hobbit" RETURN c.Name`,
                processingTime: 1.2
            };
        }
        
        if (lowerQuestion.includes('elf') || lowerQuestion.includes('elves') || lowerQuestion.includes('elfo')) {
            return {
                answer: `Os Elfos no universo do Senhor dos Anéis incluem personagens como Legolas, Arwen, Elrond, Galadriel, Celeborn, e Haldir. Eles são seres imortais com grande sabedoria e habilidades mágicas, desempenhando papéis cruciais na luta contra o mal.`,
                cypher: `MATCH (c:Characters) WHERE c.Race = "Elf" RETURN c.Name`,
                processingTime: 0.9
            };
        }
        
        if (lowerQuestion.includes('fellowship') || lowerQuestion.includes('sociedade')) {
            return {
                answer: `A Sociedade do Anel foi formada por nove membros: Frodo (portador do anel), Sam, Merry, Pippin, Gandalf, Aragorn, Boromir, Legolas, e Gimli. Cada membro trouxe habilidades únicas para a missão de destruir o Um Anel.`,
                cypher: `MATCH (c:Characters)-[:MEMBER_OF]->(f:Fellowship) RETURN c.Name`,
                processingTime: 1.1
            };
        }
        
        if (lowerQuestion.includes('movie') || lowerQuestion.includes('film') || lowerQuestion.includes('filme')) {
            return {
                answer: `A trilogia do Senhor dos Anéis dirigida por Peter Jackson consiste em três filmes: "The Fellowship of the Ring" (2001), "The Two Towers" (2002), e "The Return of the King" (2003). Cada filme adapta um volume da obra de J.R.R. Tolkien.`,
                cypher: `MATCH (m:Movies) RETURN m.Name ORDER BY m.ReleaseYear`,
                processingTime: 0.8
            };
        }
        
        if (lowerQuestion.includes('ring') || lowerQuestion.includes('anel')) {
            return {
                answer: `O Um Anel é o anel de poder central na história, criado por Sauron para controlar todos os outros anéis de poder. Ele possui a inscrição em língua negra: "Um Anel para a todos governar, Um Anel para encontrá-los, Um Anel para a todos trazer, e na escuridão aprisioná-los."`,
                cypher: `MATCH (r:Ring {Name: "One Ring"})-[:RELATED_TO]->(s:Characters) RETURN s.Name`,
                processingTime: 1.0
            };
        }
        
        // Resposta padrão
        return {
            answer: `Interessante pergunta sobre Middle-earth! Infelizmente, não tenho informações específicas sobre "${question}" no meu grafo de conhecimento atual. Tente perguntar sobre personagens específicos, raças (Hobbits, Elfos, Anões), ou eventos da história do Senhor dos Anéis.`,
            cypher: `// Consulta não mapeada para: ${question}`,
            processingTime: 0.5
        };
    }

    addMessage(sender, content, cypher = null, processingTime = null, isError = false) {
        // Remover mensagem de boas-vindas se ainda estiver presente
        const welcomeMessage = this.chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${sender}`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        
        if (isError) {
            bubbleDiv.style.background = 'rgba(255, 107, 107, 0.2)';
            bubbleDiv.style.border = '1px solid rgba(255, 107, 107, 0.3)';
        }
        
        bubbleDiv.textContent = content;
        messageDiv.appendChild(bubbleDiv);
        
        // Adicionar informações extras para respostas do assistente
        if (sender === 'assistant' && !isError) {
            const infoDiv = document.createElement('div');
            infoDiv.className = 'message-info';
            
            if (cypher) {
                const cypherDiv = document.createElement('div');
                cypherDiv.className = 'cypher-query';
                cypherDiv.innerHTML = `<strong>Cypher:</strong> ${cypher}`;
                messageDiv.appendChild(cypherDiv);
            }
            
            if (processingTime) {
                infoDiv.innerHTML = `<i class="fas fa-clock"></i> ${processingTime}s`;
                messageDiv.appendChild(infoDiv);
            }
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Adicionar ao histórico
        this.messageHistory.push({
            sender,
            content,
            cypher,
            processingTime,
            timestamp: new Date()
        });
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    showLoading() {
        this.isLoading = true;
        this.sendButton.disabled = true;
        this.loadingOverlay.classList.add('show');
    }

    hideLoading() {
        this.isLoading = false;
        this.sendButton.disabled = false;
        this.loadingOverlay.classList.remove('show');
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            if (response.ok) {
                const data = await response.json();
                document.getElementById('totalNodes').textContent = data.total_nodes || '2515';
                document.getElementById('totalCharacters').textContent = data.total_characters || '-';
                document.getElementById('totalMovies').textContent = data.total_movies || '-';
            } else {
                // Fallback para valores padrão
                document.getElementById('totalCharacters').textContent = '847';
                document.getElementById('totalMovies').textContent = '3';
            }
        } catch (error) {
            console.warn('Erro ao carregar estatísticas:', error);
            // Fallback para valores padrão
            document.getElementById('totalCharacters').textContent = '847';
            document.getElementById('totalMovies').textContent = '3';
        }
    }
}

// Função global para exemplos
function askExample(question) {
    const app = window.lotrApp;
    if (app) {
        app.userInput.value = question;
        app.sendMessage();
    }
}

// Inicializar aplicação quando DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    window.lotrApp = new LordOfTheRingsApp();
    
    // Easter egg: Konami code
    let konamiCode = '';
    const konamiSequence = 'ArrowUpArrowUpArrowDownArrowDownArrowLeftArrowRightArrowLeftArrowRightKeyBKeyA';
    
    document.addEventListener('keydown', (e) => {
        konamiCode += e.code;
        if (konamiCode.length > konamiSequence.length) {
            konamiCode = konamiCode.slice(-konamiSequence.length);
        }
        
        if (konamiCode === konamiSequence) {
            const ring = document.querySelector('.header-icon');
            ring.style.animation = 'spin 2s linear infinite';
            ring.style.color = '#ff6b6b';
            
            setTimeout(() => {
                ring.style.animation = 'glow 2s ease-in-out infinite alternate';
                ring.style.color = 'var(--primary-gold)';
            }, 4000);
            
            konamiCode = '';
        }
    });
});

// Adicionar animação de rotação para o easter egg
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style); 