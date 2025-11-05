import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class to handle all environment variables and settings."""
    
    def __init__(self):
        # Ollama configuration
        self.ollama_host = self._get_ollama_host()
        self.ollama_model = os.getenv('OLLAMA_MODEL')
        
        if not self.ollama_model:
            raise ValueError("OLLAMA_MODEL environment variable is required")
        
        # File paths
        folder_path = os.getenv("FOLDER_PATH")
        file_path = os.getenv("FILE_PATH")
        
        if not folder_path:
            raise ValueError("FOLDER_PATH environment variable is required")
        if not file_path:
            raise ValueError("FILE_PATH environment variable is required")
            
        self.folder_path = Path(folder_path)
        self.file_path = Path(file_path)

        # LLM params
        self.top_p = os.getenv("TOP_P")
        self.temperature = os.getenv("TEMPERATURE")
        self.repeat_penaly = os.getenv("PENALTY")
        self.max_new_tokens = os.getenv("MAX_NEW_TOKENS")
    
    def _get_ollama_host(self):
        """Get the Ollama host with proper defaults and Windows compatibility."""
        ollama_host = os.environ.get('OLLAMA_HOST')
        
        if not ollama_host:
            raise ValueError("OLLAMA_HOST environment variable is required")
        
        # Fix for Ollama connectivity issue
        # Use localhost instead of 0.0.0.0 for better Windows compatibility
        if ollama_host == '0.0.0.0:11434':
            ollama_host = 'localhost:11434'
        
        if not ollama_host.startswith(('http://', 'https://')):
            return f"http://{ollama_host}"
        else:
            return ollama_host

# Create a global configuration instance
config = Config()