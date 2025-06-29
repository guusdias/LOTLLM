from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import time
import json
from datetime import datetime
import traceback

from main import get_neo4j_connection, get_llm, create_cypher_chain, create_rag_chain, run_cypher_query

app = Flask(__name__)
CORS(app)  

graph = None
llm = None
cypher_chain = None
rag_chain = None
initialization_error = None

def initialize_system():
    """Inicializa o sistema RAG"""
    global graph, llm, cypher_chain, rag_chain, initialization_error
    try:
        print("Inicializando sistema RAG...")
        graph = get_neo4j_connection()
        llm = get_llm()
        cypher_chain = create_cypher_chain(llm)
        rag_chain = create_rag_chain(graph, cypher_chain, llm)
        print("Sistema RAG inicializado com sucesso!")
        return True
    except Exception as e:
        initialization_error = str(e)
        print(f"Erro na inicialização: {e}")
        return False

initialize_system()

@app.route('/')
def index():
    """Servir a página principal"""
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Servir arquivos estáticos do frontend"""
    return send_from_directory('frontend', filename)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Verificar o status da API"""
    return jsonify({
        'status': 'ok' if graph else 'error',
        'timestamp': datetime.now().isoformat(),
        'neo4j_connected': graph is not None,
        'llm_connected': llm is not None,
        'initialization_error': initialization_error
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Obter estatísticas do grafo"""
    if not graph:
        return jsonify({'error': 'Sistema não inicializado'}), 500
    
    try:
        # Contar total de nós
        total_nodes = graph.query("MATCH (n) RETURN count(n) as total")[0]['total']
        
        # Contar personagens
        characters = graph.query("MATCH (c:Characters) RETURN count(c) as total")[0]['total']
        
        # Contar filmes
        movies = graph.query("MATCH (m:Movies) RETURN count(m) as total")[0]['total']
        
        # Contar relacionamentos
        relationships = graph.query("MATCH ()-[r]->() RETURN count(r) as total")[0]['total']
        
        return jsonify({
            'total_nodes': total_nodes,
            'total_characters': characters,
            'total_movies': movies,
            'total_relationships': relationships,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao obter estatísticas: {str(e)}'}), 500

@app.route('/api/query', methods=['POST'])
def query_knowledge_graph():
    """Processar pergunta sobre o grafo de conhecimento"""
    if not rag_chain:
        return jsonify({
            'error': 'Sistema RAG não inicializado',
            'initialization_error': initialization_error
        }), 500
    
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({'error': 'Pergunta não fornecida'}), 400
        
        start_time = time.time()
        
        cypher_query = cypher_chain.invoke({"question": question})
        
        if cypher_query.startswith("```cypher"):
            cypher_query = cypher_query.replace("```cypher", "", 1)
        if cypher_query.endswith("```"):
            cypher_query = cypher_query[:-3]
        cypher_query = cypher_query.strip()
        
        response = rag_chain.invoke(question)
        
        processing_time = round(time.time() - start_time, 2)
        
        return jsonify({
            'answer': response,
            'cypher_query': cypher_query,
            'processing_time': processing_time,
            'timestamp': datetime.now().isoformat(),
            'question': question
        })
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Erro ao processar pergunta: {error_trace}")
        
        return jsonify({
            'error': f'Erro ao processar pergunta: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/examples', methods=['GET'])
def get_example_questions():
    """Obter perguntas de exemplo"""
    examples = [
        {
            'question': 'List all characters who are Hobbits',
            'category': 'Characters',
            'description': 'Encontrar todos os personagens da raça Hobbit'
        },
        {
            'question': 'Which characters appear in Fellowship of the Ring?',
            'category': 'Movies',
            'description': 'Personagens que aparecem no primeiro filme'
        },
        {
            'question': 'How many Elves are in the movies?',
            'category': 'Statistics',
            'description': 'Contar personagens da raça Élfica'
        },
        {
            'question': 'Who are the members of the Fellowship?',
            'category': 'Fellowship',
            'description': 'Membros da Sociedade do Anel'
        },
        {
            'question': 'What movies are in the database?',
            'category': 'Movies',
            'description': 'Listar todos os filmes disponíveis'
        }
    ]
    
    return jsonify(examples)

@app.route('/api/reset', methods=['POST'])
def reset_system():
    """Reinicializar o sistema (útil para desenvolvimento)"""
    global initialization_error
    initialization_error = None
    
    success = initialize_system()
    
    return jsonify({
        'success': success,
        'message': 'Sistema reinicializado com sucesso!' if success else 'Falha na reinicialização',
        'error': initialization_error if not success else None,
        'timestamp': datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint não encontrado'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    ports_to_try = [9342]
    
    for port in ports_to_try:
        try:
            print("=== Lord of the Rings Knowledge Graph API ===")
            print(f"Frontend disponível em: http://localhost:{port}")
            print(f"API Health Check: http://localhost:{port}/api/health")
            print(f"API Stats: http://localhost:{port}/api/stats")
            print("=" * 50)
            
            debug_mode = os.getenv('FLASK_ENV') == 'development'
            app.run(host='0.0.0.0', port=port, debug=debug_mode)
            break  
        except OSError as e:
            if "Address already in use" in str(e):
                print(f"Porta {port} já está em uso, tentando próxima...")
                continue
            else:
                raise e
    else:
        print("❌ Erro: Não foi possível encontrar uma porta disponível!")
        print("💡 Sugestão: Desabilite o AirPlay Receiver em Configurações > Geral > AirDrop e Handoff") 