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
        
        # Training data storage
        self.training_data_file = 'chatbot_training_data.json'
        self.custom_knowledge = self._load_custom_training_data()
    
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
    
    def _load_custom_training_data(self):
        """Load custom training data added by admin"""
        try:
            import json
            if os.path.exists(self.training_data_file):
                with open(self.training_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('custom_knowledge', '')
            return ''
        except Exception as e:
            logger.error(f"Error loading training data: {e}")
            return ''
    
    def add_training_data(self, new_data: str):
        """Add new training data to the knowledge base"""
        try:
            import json
            from datetime import datetime
            existing_data = {'custom_knowledge': self.custom_knowledge}
            
            if os.path.exists(self.training_data_file):
                with open(self.training_data_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            # Append new data
            current_knowledge = existing_data.get('custom_knowledge', '')
            updated_knowledge = current_knowledge + "\n\n" + new_data if current_knowledge else new_data
            existing_data['custom_knowledge'] = updated_knowledge
            existing_data['last_updated'] = datetime.now().isoformat()
            
            with open(self.training_data_file, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, indent=2)
            
            # Update in-memory knowledge
            self.custom_knowledge = updated_knowledge
            return True
        except Exception as e:
            logger.error(f"Error adding training data: {e}")
            return False
    
    def get_training_data(self):
        """Get current training data"""
        try:
            import json
            if os.path.exists(self.training_data_file):
                with open(self.training_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {'custom_knowledge': '', 'last_updated': None}
        except Exception as e:
            logger.error(f"Error getting training data: {e}")
            return {'custom_knowledge': '', 'last_updated': None}
    
    def reset_training_data(self):
        """Reset custom training data"""
        try:
            import json
            with open(self.training_data_file, 'w', encoding='utf-8') as f:
                json.dump({'custom_knowledge': '', 'last_updated': None}, f)
            self.custom_knowledge = ''
            return True
        except Exception as e:
            logger.error(f"Error resetting training data: {e}")
            return False
    
    def ask_question(self, question: str, conversation_history=None, **kwargs):
        """
        Answer diabetes-related questions using Groq LLM
        
        Args:
            question: User's health question
            conversation_history: List of previous messages for context (optional)
            
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
            
            # Build conversation context if available
            context_section = ""
            if conversation_history and len(conversation_history) > 0:
                context_section = "\n\nCONVERSATION HISTORY (for context):\n"
                for msg in conversation_history[-6:]:  # Last 3 exchanges (6 messages)
                    role = "User" if msg.get('role') == 'user' else "Assistant"
                    context_section += f"{role}: {msg.get('content', '')}\n"
            
            # Add custom training data if available
            custom_section = ""
            if self.custom_knowledge:
                custom_section = f"\n\nADDITIONAL TRAINING DATA:\n{self.custom_knowledge}"
            
            # Create advanced health assistant prompt (ChatGPT-style)
            prompt = f"""You are an advanced AI Health Assistant specializing in diabetes and wellness.

YOUR CAPABILITIES:
• Provide accurate, evidence-based medical information
• Explain complex health concepts in simple terms
• Offer personalized lifestyle and dietary recommendations
• Answer questions about diabetes, symptoms, prevention, and management
• Provide emotional support and encouragement

RESPONSE STYLE:
✓ Professional yet conversational and warm
✓ Clear, well-structured responses with bullet points or numbered lists when helpful
✓ Concise but comprehensive (2-5 paragraphs)
✓ Use emojis sparingly for friendliness (💡 🏥 📊 ✅)
✓ Provide actionable advice with specific examples
✓ Each response should be unique and tailored to the question
✓ Use markdown formatting for better readability (**bold**, *italic*, lists)

IMPORTANT GUIDELINES:
⚠️ Always remind users to consult healthcare professionals for diagnosis and treatment
⚠️ Never diagnose conditions or prescribe medications
⚠️ Be empathetic when discussing health concerns
⚠️ Admit when you don't know something

KNOWLEDGE BASE:
{self.diabetes_knowledge}{custom_section}
{context_section}

USER QUESTION:
{question}

YOUR RESPONSE (provide a clear, helpful, and well-formatted answer):"""

            # Get response from Groq with temperature for variety
            from langchain_core.messages import HumanMessage, SystemMessage
            
            messages = [
                SystemMessage(content="You are an advanced AI Health Assistant. Provide unique, well-formatted, and personalized responses to each question. Use markdown formatting, bullet points, and emojis appropriately. Never give repetitive or generic answers. Always tailor your response to the specific user question."),
                HumanMessage(content=prompt)
            ]
            
            # Use temperature 0.7 for more varied responses while maintaining accuracy
            response = self.llm.invoke(messages)
            answer = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "answer": answer.strip(),
                "error": False
            }
            
        except Exception as e:
            logger.error(f"Chatbot error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "answer": "I apologize, but I'm experiencing technical difficulties right now. Please try asking your question again in a moment. If this continues, please contact support.",
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
