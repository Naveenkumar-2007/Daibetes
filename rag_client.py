"""
RAG Chatbot Client
Connects the diabetes prediction website to the RAG backend
"""
import requests
import logging

logger = logging.getLogger(__name__)


class RAGClient:
    """Client to communicate with the RAG chatbot backend"""
    
    def __init__(self, rag_backend_url="http://localhost:5001"):
        """
        Initialize RAG client
        
        Args:
            rag_backend_url: URL where the RAG Flask app is running
        """
        self.backend_url = rag_backend_url.rstrip('/')
        self.ask_endpoint = f"{self.backend_url}/ask"
    
    def ask_question(self, question: str, agentic: bool = True, timeout: int = 30):
        """
        Send a question to the RAG chatbot
        
        Args:
            question: User's question
            agentic: Whether to use agentic mode (ReAct agent)
            timeout: Request timeout in seconds
            
        Returns:
            dict: Response with 'answer' key, or error dict
        """
        try:
            response = requests.post(
                self.ask_endpoint,
                json={
                    "message": question,
                    "agentic": agentic
                },
                timeout=timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"RAG backend returned status {response.status_code}")
                return {
                    "answer": "Sorry, the medical assistant is currently unavailable. Please try again later.",
                    "error": True
                }
                
        except requests.exceptions.Timeout:
            logger.error("RAG backend request timed out")
            return {
                "answer": "The request took too long. Please try asking a simpler question.",
                "error": True
            }
            
        except requests.exceptions.ConnectionError:
            logger.error("Could not connect to RAG backend")
            return {
                "answer": "Sorry, I cannot connect to the medical assistant service. Please make sure it's running.",
                "error": True
            }
            
        except Exception as e:
            logger.error(f"RAG client error: {str(e)}")
            return {
                "answer": "An unexpected error occurred. Please try again.",
                "error": True
            }
    
    def health_check(self):
        """
        Check if the RAG backend is accessible
        
        Returns:
            bool: True if backend is reachable
        """
        try:
            response = requests.get(f"{self.backend_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False


# Global instance
rag_client = RAGClient()
