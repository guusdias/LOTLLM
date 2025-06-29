import os
from dotenv import load_dotenv
from langchain_neo4j import Neo4jGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import GraphCypherQAChain
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


load_dotenv()

def get_neo4j_connection():
    """Inicializa e testa a conexão com Neo4j"""
    neo4j_uri = os.getenv("NEO4J_URI")
    neo4j_user = os.getenv("NEO4J_USER")
    neo4j_password = os.getenv("NEO4J_PASSWORD")
    
    if not all([neo4j_uri, neo4j_user, neo4j_password]):
        raise ValueError("Variáveis de ambiente Neo4j não configuradas. Verifique NEO4J_URI, NEO4J_USER e NEO4J_PASSWORD")
    
    graph = Neo4jGraph(
        url=neo4j_uri,
        username=neo4j_user,
        password=neo4j_password
    )
    
    try:
        test_result = graph.query("MATCH (n) RETURN count(n)")
        print(f"Conexão com Neo4j estabelecida com sucesso: {test_result}")
        return graph
    except Exception as e:
        print(f"Erro na conexão com Neo4j: {e}")
        raise

def get_llm():
    """Inicializa o modelo de linguagem"""
    google_api_key = os.getenv("GOOGLE_API_KEY")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    temperature = float(os.getenv("MODEL_TEMPERATURE", "0.0"))
    
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY não configurada nas variáveis de ambiente")
    
    return ChatGoogleGenerativeAI(
        model=gemini_model,
        temperature=temperature,
        google_api_key=google_api_key
    )

def create_cypher_chain(llm):
    """Cria a chain para geração de consultas Cypher"""
    cypher_prompt = PromptTemplate.from_template(
        """
        You are an expert in Neo4j Cypher queries. The graph contains nodes labeled Movies, Characters, Chapters, and Scripts, with relationships like ACTED_IN, APPEAR_IN, SPLIT_IN, USE_IN, and SPOKE_IN.
        Node properties include:
        - Movies: Name (e.g., "The Fellowship Of The Ring")
        - Characters: Name, Race (e.g., "Galadriel", "Elf")
        Use partial matches for movie titles (e.g., CONTAINS "Fellowship Of The Ring" or "Two Towers") unless an exact title is specified.
        Based on the following question, generate a valid Cypher query to retrieve relevant data.
        Examples:
        Question: "Which characters are in Lord of the Rings movies?"
        Cypher: MATCH (c:Characters)-[:ACTED_IN]->(m:Movies) WHERE m.Name CONTAINS "Of The Ring" OR m.Name CONTAINS "Two Towers" OR m.Name CONTAINS "Return Of The King" RETURN c.Name, m.Name
        Question: "How many hobbits are in Lord of the Rings?"
        Cypher: MATCH (c:Characters)-[:ACTED_IN]->(m:Movies) WHERE c.Race = "Hobbit" AND (m.Name CONTAINS "Of The Ring" OR m.Name CONTAINS "Two Towers" OR m.Name CONTAINS "Return Of The King") RETURN count(DISTINCT c)
        Question: {question}
        Output only the Cypher query.
        """
    )
    
    return cypher_prompt | llm | StrOutputParser()

def run_cypher_query(question, graph, cypher_chain):
    """Executa uma consulta Cypher baseada na pergunta"""
    try:
        cypher_query = cypher_chain.invoke({"question": question})
        print(f"Cypher gerado: {cypher_query}")

        
        if cypher_query.startswith("```cypher"):
            cypher_query = cypher_query.replace("```cypher", "", 1)
        if cypher_query.endswith("```"):
            cypher_query = cypher_query[:-3]

        cypher_query = cypher_query.strip()

        print(f"Executando Cypher: {cypher_query}")
        results = graph.query(cypher_query)
        print(f"Resultados da consulta: {results}")
        
        if not results:
            return "Nenhum dado encontrado no grafo."
        return results
    except Exception as e:
        return f"Erro ao executar consulta Cypher: {e}"

def create_rag_chain(graph, cypher_chain, llm):
    """Cria a chain RAG para responder perguntas"""
    prompt = ChatPromptTemplate.from_template(
        """
        You are an assistant that answers questions based on a Lord of the Rings knowledge graph.

        Question: {question}
        Data retrieved from the graph (already filtered by the Cypher query): {context}

        The data above was retrieved using a Cypher query that already filtered the results based on the question.
        If the data contains character names, they have already been filtered according to the search criteria.

        Answer the question directly based on this filtered data. If there are multiple results, list them clearly.
        If the data is empty, explain that no matching records were found in the graph.
        """
    )

    return (
        {"context": lambda x: run_cypher_query(x, graph, cypher_chain), "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

def main():
    """Função principal"""
    try:
        print("Inicializando conexões...")
        graph = get_neo4j_connection()
        llm = get_llm()
        cypher_chain = create_cypher_chain(llm)
        rag_chain = create_rag_chain(graph, cypher_chain, llm)

        print("Sistema pronto! Digite 'exit' para sair.")

        while True:
            question = input("\nFaça sua pergunta (ou 'exit' para sair): ")
            if question.lower() == 'exit':
                break
            
            try:
                response = rag_chain.invoke(question)
                print(f"\nResposta: {response}")
            except Exception as e:
                print(f"Erro ao processar pergunta: {e}")

    except Exception as e:
        print(f"Erro na inicialização: {e}")
        print("Verifique se as variáveis de ambiente estão configuradas corretamente.")

if __name__ == "__main__":
    main()
