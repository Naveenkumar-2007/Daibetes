"""
Integrated RAG Chatbot - Uses Groq LLM directly (No separate backend needed)
"""
import os
import logging
from typing import Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


class IntegratedChatbot:
    """
    Integrated chatbot that uses the same Groq LLM as the main app
    No separate RAG backend needed - everything runs in one Flask app
    """
    
    def __init__(self, llm=None):
        """
        Initialize with the existing LLM instance from flask_app
        
        Args:
            llm: The Groq LLM instance (passed from flask_app)
        """
        self.llm = llm
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        
        # Medical knowledge base
        self.diabetes_knowledge = self._load_diabetes_knowledge()
    
    def _load_diabetes_knowledge(self):
        """Load basic diabetes knowledge for the chatbot"""
        return """
        # Diabetes Health Knowledge Base
        
        ## What is Diabetes?
        Diabetes is a chronic disease that occurs when the pancreas cannot produce enough insulin or when the body cannot effectively use the insulin it produces. Insulin is a hormone that regulates blood glucose levels.
        
        ## Types of Diabetes:
        1. **Type 1 Diabetes**: The pancreas produces little or no insulin. It usually develops in children and young adults.
        2. **Type 2 Diabetes**: The body doesn't use insulin properly (insulin resistance). This is the most common type.
        3. **Gestational Diabetes**: Occurs during pregnancy and usually disappears after delivery.
        
        ## Common Symptoms:
        - Increased thirst and frequent urination
        - Extreme hunger
        - Unexplained weight loss
        - Fatigue
        - Blurred vision
        - Slow-healing sores
        - Frequent infections
        
        ## Blood Sugar Levels (Glucose):
        - **Normal fasting**: 70-99 mg/dL
        - **Prediabetes**: 100-125 mg/dL
        - **Diabetes**: 126 mg/dL or higher
        
        ## Risk Factors:
        - Family history of diabetes
        - Being overweight or obese
        - Age (45 years or older)
        - Physical inactivity
        - High blood pressure
        - High cholesterol
        - History of gestational diabetes
        
        ## Prevention Tips:
        - Maintain a healthy weight
        - Exercise regularly (150 minutes per week)
        - Eat a balanced diet rich in vegetables, fruits, whole grains
        - Limit sugar and processed foods
        - Stay hydrated
        - Get regular health checkups
        - Manage stress
        - Get adequate sleep (7-9 hours)
        
        ## Foods to Include:
        - Leafy green vegetables (spinach, kale)
        - Whole grains (brown rice, quinoa, oats)
        - Fatty fish (salmon, sardines)
        - Nuts and seeds
        - Berries
        - Greek yogurt
        - Legumes (beans, lentils)
        
        ## Foods to Limit:
        - Sugary drinks
        - White bread and pasta
        - Fried foods
        - Processed snacks
        - Candy and desserts
        - High-sodium foods
        
        ## Lab Tests:
        - **HbA1c**: Measures average blood sugar over 2-3 months
        - **Fasting Blood Glucose**: Measures blood sugar after overnight fasting
        - **Oral Glucose Tolerance Test**: Measures body's response to sugar
        
        ## Complications (if untreated):
        - Heart disease
        - Kidney damage
        - Eye damage (retinopathy)
        - Nerve damage (neuropathy)
        - Foot problems
        - Skin conditions
        
        ## Lifestyle Management:
        - Monitor blood sugar regularly
        - Take medications as prescribed
        - Follow meal plans
        - Exercise consistently
        - Manage stress through yoga, meditation
        - Avoid smoking and limit alcohol
        - Regular doctor visits
        """
    
    def ask_question(self, question: str, **kwargs):
        """
        Answer diabetes-related questions using Groq LLM
        
        Args:
            question: User's health question
            
        Returns:
            dict: Response with 'answer' key
        """
        try:
            # Check if LLM is available
            if not self.llm:
                return {
                    "answer": "Hi! I'm your diabetes health assistant. I can help answer questions about diabetes, symptoms, prevention, diet, and lifestyle tips. What would you like to know?",
                    "error": False
                }
            
            # Create medical assistant prompt
            prompt = f"""You are a friendly, professional **Diabetes & Health Assistant**.

Your job is to provide clear, helpful information about diabetes, health, and wellness.

IMPORTANT GUIDELINES:
- Use simple, easy-to-understand language
- Keep answers short and to the point (2-4 paragraphs)
- Provide practical, actionable advice
- Never diagnose or prescribe - remind users to consult healthcare professionals for medical advice
- Be warm, empathetic, and encouraging
- If unsure, admit it honestly

KNOWLEDGE BASE:
{self.diabetes_knowledge}

USER QUESTION:
{question}

ANSWER (be helpful, clear, and concise):"""

            # Get response from Groq
            from langchain_core.messages import HumanMessage
            
            response = self.llm.invoke([HumanMessage(content=prompt)])
            answer = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "answer": answer,
                "error": False
            }
            
        except Exception as e:
            logger.error(f"Chatbot error: {str(e)}")
            return {
                "answer": f"I'm having trouble right now. Please try again in a moment. If the issue persists, contact support.",
                "error": True
            }
    
    def health_check(self):
        """
        Check if chatbot is ready
        
        Returns:
            bool: True if LLM is configured
        """
        return self.llm is not None


# Global instance (will be initialized with LLM from flask_app)
chatbot = None
