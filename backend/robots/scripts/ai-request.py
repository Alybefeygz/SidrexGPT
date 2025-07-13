#!/usr/bin/env python3
"""
AI Request Script for SidrexGPT Robots App - OpenRouter Integration
"""

import requests
import json
import logging
import os
import time
import random
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Available models with fallback
MODELS = [
    "deepseek/deepseek-r1-distill-llama-70b:free" # Sadece bu modeli kullan
]

class OpenRouterAIHandler:
    """
    Handler class for OpenRouter AI API requests
    """
    
    def __init__(self, api_key: Optional[str] = None, app_name: str = "SidrexGPT"):
        """
        Initialize the OpenRouter AI Handler
        
        Args:
            api_key: OpenRouter API key (REQUIRED)
            app_name: Application name for the requests
        """
        if not api_key:
            raise ValueError("❌ OpenRouter API key is required! Please provide a valid API key.")
        
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.app_name = app_name
        self.session = requests.Session()
        self.current_model_index = 0  # Track current model index
        self.model_error_counts = {model: 0 for model in MODELS}  # Track errors per model
        
        # Set headers for OpenRouter
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",  # SidrexGPT local development
            "X-Title": self.app_name
        })
    
    
    
    def make_chat_request(self, messages: list, model: str = None, max_tokens: int = 10000) -> Dict[str, Any]:
        """
        Make a chat completion request to OpenRouter without model rotation.
        
        Args:
            messages: List of chat messages
            model: Model to use (if None, will use the first model in MODELS)
            max_tokens: Maximum tokens for response (default 10000)
            
        Returns:
            Response data as dictionary
        """
        if model is None:
            model = MODELS[0]  # Use the first (and only) model

        url = f"{self.base_url}/chat/completions"

        data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

        # Debug: İstek verilerini logla (stderr'e yönlendirildi)
        import sys
        total_content_length = sum(len(msg.get('content', '')) for msg in messages)
        print(f"DEBUG OpenRouter İsteği - Model: {model}", file=sys.stderr)
        print(f"DEBUG OpenRouter İsteği - Max Tokens: {max_tokens}", file=sys.stderr)
        print(f"DEBUG OpenRouter İsteği - Toplam İçerik Uzunluğu: {total_content_length} karakter", file=sys.stderr)
        print(f"DEBUG OpenRouter İsteği - Mesaj Sayısı: {len(messages)}", file=sys.stderr)

        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()

            logger.info(f"Successful chat request with model: {model}")

            # Debug: Yanıt bilgilerini logla
            response_data = response.json()
            if 'choices' in response_data and response_data['choices']:
                response_content = response_data['choices'][0]['message']['content']
                print(f"DEBUG OpenRouter Yanıtı - İçerik Uzunluğu: {len(response_content)} karakter")
                print(f"DEBUG OpenRouter Yanıtı - İlk 100 karakter: {response_content[:100]}")

            if 'usage' in response_data:
                usage = response_data['usage']
                print(f"DEBUG OpenRouter Yanıtı - Token Kullanımı: {usage}")

            return response_data

        except requests.exceptions.HTTPError as e:
            logger.error(f"Chat request failed with {model} (HTTP Error): {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 429:
                return {"error": "AI hizmeti şu anda yoğun. Lütfen daha sonra tekrar deneyin."}
            else:
                return {"error": f"AI hizmetinden bir hata oluştu: {e.response.status_code}"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Chat request failed with {model} (Request Error): {e}")
            return {"error": f"AI hizmetine bağlanırken hata: {e}"}
        except Exception as e:
            logger.error(f"Chat request failed with {model} (General Error): {e}")
            return {"error": f"AI yanıtı alınırken genel bir hata oluştu: {e}"}
    
    def get_available_models(self) -> Dict[str, Any]:
        """
        Get list of available models from OpenRouter
        
        Returns:
            Dictionary containing available models
        """
        try:
            url = f"{self.base_url}/models"
            response = self.session.get(url)
            response.raise_for_status()
            
            logger.info("Successfully retrieved available models")
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get models: {e}")
            raise
    
    def ask_question(self, question: str, model: str = None, system_prompt: Optional[str] = None, max_tokens: int = 10000) -> str:
        """
        Ask a simple question to the AI
        
        Args:
            question: The question to ask
            model: Model to use (if None, will use model rotation)
            system_prompt: Optional system prompt to set AI behavior
            max_tokens: Maximum tokens for response (default 10000)
            
        Returns:
            AI response as string
        """
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add user question
        messages.append({"role": "user", "content": question})
        
        try:
            response = self.make_chat_request(messages, model, max_tokens=max_tokens)
            
            # Check if response contains an error
            if "error" in response:
                return response["error"]
            
            ai_response = response["choices"][0]["message"]["content"]
            
            logger.info(f"Question: {question[:50]}...")
            logger.info(f"Response: {ai_response[:100]}...")
            
            return ai_response
            
        except Exception as e:
            logger.error(f"Error asking question: {e}")
            return f"Üzgünüm, şu anda teknik bir sorun yaşıyorum. Lütfen daha sonra tekrar deneyin."
    
    def chat_with_history(self, messages: list, model: str = None, max_tokens: int = 4000) -> str:
        """
        Chat with conversation history.
        RAISES:
            ValueError: If the AI response contains an error or fails.
        """
        try:
            response = self.make_chat_request(messages, model, max_tokens=max_tokens)
            
            # If the response dictionary itself contains an error key, raise an exception.
            if "error" in response:
                raise ValueError(response["error"])
            
            # Check for valid response structure
            if "choices" not in response or not response.get("choices"):
                raise ValueError(f"AI response is malformed or empty. Response: {response}")
                
            return response["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            # Re-raise network errors as a specific ValueError
            logger.error(f"Network error during chat with history: {e}")
            raise ValueError(f"AI service network error: {e}")
        except Exception as e:
            # Catch any other exception and re-raise it to be handled by the main function.
            logger.error(f"Error in chat_with_history: {e}")
            # Re-raise the exception to ensure the script exits with an error code.
            raise


def test_openrouter():
    """
    Test function for OpenRouter API
    """
    print("🤖 SidrexGPT - OpenRouter AI Test Starting...")
    print("=" * 50)
    
    # Try to get API key from Django settings if available
    api_key = None
    try:
        # Try to load Django settings
        import sys
        import os
        
        # Add the backend directory to Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(os.path.dirname(current_dir))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)
        
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
        import django
        django.setup()
        
        from django.conf import settings
        api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        
        if api_key:
            print(f"✅ API key loaded from Django settings")
        else:
            print("⚠️  No API key found in Django settings")
            
    except Exception as e:
        print(f"⚠️  Could not load Django settings: {e}")
        # Fallback to environment variable
        api_key = os.getenv('OPENROUTER_API_KEY')
        if api_key:
            print(f"✅ API key loaded from environment")
        else:
            print("❌ No API key found in environment either")
            return
    
    if not api_key:
        print("❌ No API key available for testing")
        return

    # Initialize handler
    ai_handler = OpenRouterAIHandler(api_key=api_key)
    
    # Test 1: Get available models
    print("\n📋 Available Models:")
    try:
        models = ai_handler.get_available_models()
        free_models = [model for model in models.get('data', []) if 'free' in model.get('id', '').lower()]
        print(f"Total models: {len(models.get('data', []))}")
        print(f"Free models found: {len(free_models)}")
        if free_models:
            print("Some free models:")
            for model in free_models[:3]:
                print(f"  - {model.get('id', 'Unknown')}")
    except Exception as e:
        print(f"Error getting models: {e}")
    
    # Test 2: Simple question
    print("\n❓ Testing Simple Question:")
    question = "Merhaba! Sen kimsin?"
    print(f"Question: {question}")
    
    try:
        answer = ai_handler.ask_question(question)
        print(f"Answer: {answer}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Question with system prompt
    print("\n🎭 Testing with System Prompt:")
    system_prompt = "Sen SidrexGPT'nin yardımcı yapay zeka asistanısın. Türkçe yanıt ver ve yardımcı ol."
    question2 = "Python programlama hakkında kısa bilgi verir misin?"
    
    try:
        answer2 = ai_handler.ask_question(question2, system_prompt=system_prompt)
        print(f"Question: {question2}")
        print(f"Answer: {answer2}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Conversation history
    print("\n💬 Testing Conversation History:")
    conversation = [
        {"role": "system", "content": "Sen yardımcı bir AI asistanısın."},
        {"role": "user", "content": "Merhaba, adım Ahmet."},
        {"role": "assistant", "content": "Merhaba Ahmet! Size nasıl yardımcı olabilirim?"},
        {"role": "user", "content": "Benim adımı hatırlıyor musun?"}
    ]
    
    try:
        response = ai_handler.chat_with_history(conversation)
        print(f"AI Response: {response}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 OpenRouter AI Test Completed!")


def interactive_chat():
    """
    Interactive chat session with OpenRouter AI
    """
    print("🤖 SidrexGPT - Interactive Chat")
    print("Type 'quit' to exit")
    print("=" * 30)
    
    ai_handler = OpenRouterAIHandler()
    conversation = [
        {"role": "system", "content": "Sen SidrexGPT'nin yardımcı yapay zeka asistanısın. Türkçe yanıt ver, yardımcı ve samimi ol."}
    ]
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'çıkış']:
                print("👋 Hoşça kal!")
                break
            
            if not user_input:
                continue
            
            # Add user message to conversation
            conversation.append({"role": "user", "content": user_input})
            
            # Get AI response
            print("🤖 AI: ", end="", flush=True)
            ai_response = ai_handler.chat_with_history(conversation)
            print(ai_response)
            
            # Add AI response to conversation
            conversation.append({"role": "assistant", "content": ai_response})
            
        except KeyboardInterrupt:
            print("\n👋 Chat interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def main():
    """
    Main function - handles command line arguments for API integration
    """
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='SidrexGPT AI Request Handler')
    parser.add_argument('--api-key', required=False, help='OpenRouter API key')
    parser.add_argument('--prompt', required=False, help='JSON formatted messages')
    parser.add_argument('--model', help='AI model to use')
    parser.add_argument('--max-tokens', type=int, default=10000, help='Maximum tokens')
    
    # Legacy support for test/chat commands
    parser.add_argument('command', nargs='?', choices=['test', 'chat'], help='Legacy commands')
    
    try:
        args = parser.parse_args()
        
        # Handle API integration mode (--api-key and --prompt provided)
        if args.api_key and args.prompt:
            try:
                messages = json.loads(args.prompt)
                ai_handler = OpenRouterAIHandler(api_key=args.api_key)
                response = ai_handler.chat_with_history(messages, model=args.model, max_tokens=args.max_tokens)
                
                # Print response to stdout for subprocess capture
                print(response)
                return
                
            except json.JSONDecodeError as e:
                print(f"JSON Parse Error: {e}")
                sys.exit(1)
            except Exception as e:
                print(f"AI Request Error: {e}")
                sys.exit(1)
        
        # Handle legacy mode (test/chat commands)
        elif args.command:
            if args.command == "test":
                test_openrouter()
            elif args.command == "chat":
                interactive_chat()
        else:
            # Default behavior - show help or run test
            if len(sys.argv) == 1:
                test_openrouter()
            else:
                parser.print_help()
                
    except SystemExit:
        # argparse calls sys.exit on error, re-raise it
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 