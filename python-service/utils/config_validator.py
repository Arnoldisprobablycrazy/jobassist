"""
Configuration validator and setup utility for JobAssist AI services.
"""
import os
from typing import Dict, List, Tuple
from dotenv import load_dotenv

def validate_configuration() -> Tuple[bool, List[str], Dict[str, bool]]:
    """
    Validate all required environment variables and API keys.
    
    Returns:
        Tuple of (is_valid, missing_keys, service_status)
    """
    # Load environment variables
    load_dotenv()
    
    # Required configuration
    required_configs = {
        "GROQ_API_KEY": "Groq LLM API Key",
        "COHERE_API_KEY": "Cohere Embeddings API Key",
    }
    
    # Qdrant configuration (either cloud or local)
    qdrant_cloud_configs = ["QDRANT_URL", "QDRANT_API_KEY"]
    qdrant_local_configs = ["QDRANT_HOST", "QDRANT_PORT"]
    
    missing_keys = []
    service_status = {}
    
    # Check required API keys
    for key, description in required_configs.items():
        value = os.getenv(key)
        if not value or value == f"your_{key.lower()}_here":
            missing_keys.append(f"{key} ({description})")
            service_status[key] = False
        else:
            service_status[key] = True
    
    # Check Qdrant configuration
    has_cloud_config = all(os.getenv(key) and os.getenv(key) != f"your_{key.lower()}_here" 
                          for key in qdrant_cloud_configs)
    has_local_config = all(os.getenv(key) for key in qdrant_local_configs)
    
    if has_cloud_config:
        service_status["QDRANT"] = True
        service_status["QDRANT_TYPE"] = "Cloud"
    elif has_local_config:
        service_status["QDRANT"] = True
        service_status["QDRANT_TYPE"] = "Local"
    else:
        missing_keys.append("QDRANT configuration (either Cloud: QDRANT_URL + QDRANT_API_KEY or Local: QDRANT_HOST + QDRANT_PORT)")
        service_status["QDRANT"] = False
        service_status["QDRANT_TYPE"] = "None"
    
    is_valid = len(missing_keys) == 0
    
    return is_valid, missing_keys, service_status

def print_configuration_status():
    """Print detailed configuration status."""
    print("\n" + "="*60)
    print("🔧 JOBASSIST AI CONFIGURATION STATUS")
    print("="*60)
    
    is_valid, missing_keys, service_status = validate_configuration()
    
    # Print service status
    print("\n📊 SERVICE STATUS:")
    
    # Groq LLM
    groq_status = "✅ Connected" if service_status.get("GROQ_API_KEY") else "❌ Missing API Key"
    print(f"  🤖 Groq LLM:        {groq_status}")
    
    # Cohere Embeddings  
    cohere_status = "✅ Connected" if service_status.get("COHERE_API_KEY") else "❌ Missing API Key"
    print(f"  🧠 Cohere Embed:    {cohere_status}")
    
    # Qdrant Vector DB
    if service_status.get("QDRANT"):
        qdrant_type = service_status.get("QDRANT_TYPE", "Unknown")
        print(f"  🗄️  Qdrant DB:       ✅ Connected ({qdrant_type})")
    else:
        print(f"  🗄️  Qdrant DB:       ❌ Not Configured")
    
    # Overall status
    print(f"\n🎯 OVERALL STATUS:   {'✅ Ready for AI Operations' if is_valid else '⚠️  Configuration Required'}")
    
    # Missing configurations
    if missing_keys:
        print(f"\n❗ MISSING CONFIGURATION:")
        for key in missing_keys:
            print(f"  • {key}")
        
        print(f"\n📝 SETUP INSTRUCTIONS:")
        print(f"  1. Edit the .env file in python-service/")
        print(f"  2. Add your API keys from:")
        print(f"     • Groq: https://console.groq.com")
        print(f"     • Cohere: https://dashboard.cohere.ai")
        print(f"     • Qdrant Cloud: https://cloud.qdrant.io")
        print(f"  3. Restart the application")
    
    print("="*60)
    
    return is_valid

def get_api_signup_links() -> Dict[str, str]:
    """Get signup links for all required services."""
    return {
        "Groq": "https://console.groq.com",
        "Cohere": "https://dashboard.cohere.ai", 
        "Qdrant Cloud": "https://cloud.qdrant.io"
    }

def create_sample_env_file():
    """Create a sample .env file with placeholders."""
    sample_content = '''# ===============================
# AI SERVICES CONFIGURATION  
# ===============================

# Groq LLM API (https://console.groq.com)
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant

# Cohere Embeddings API (https://dashboard.cohere.ai) 
COHERE_API_KEY=your_cohere_api_key_here
COHERE_MODEL=embed-english-v3.0

# Qdrant Vector Database Cloud (https://cloud.qdrant.io)
QDRANT_URL=https://your-cluster-url.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_SIZE=1024

# ===============================
# APPLICATION SETTINGS
# ===============================

FLASK_ENV=development
FLASK_DEBUG=True
FLASK_PORT=5000'''
    
    return sample_content

if __name__ == "__main__":
    print_configuration_status()