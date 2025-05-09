from dotenv import load_dotenv
import os
from pathlib import Path
from rich.console import Console

console = Console()

def check_and_create_env():
    env_path = Path('.env')
    if not env_path.exists():
        console.print("[bold yellow]No .env file found. Let's create one.[/bold yellow]")
        
        # Get values from user with defaults
        openai_api_key = input("Enter OPENAI_API_KEY (required): ")
        while not openai_api_key:
            openai_api_key = input("OPENAI_API_KEY is required. Please enter a value: ")
            
        postgres_host = input("Enter POSTGRES_HOST (default: localhost): ") or "localhost"
        postgres_port = input("Enter POSTGRES_PORT (default: 5432): ") or "5432"
        postgres_user = input("Enter POSTGRES_USER (default: postgres): ") or "postgres"
        postgres_password = input("Enter POSTGRES_PASSWORD (default: postgres): ") or "postgres"
        postgres_db = input("Enter POSTGRES_DB (default: postgres): ") or "postgres"
        
        # Create .env file
        with open(env_path, 'w') as f:
            f.write(f"OPENAI_API_KEY={openai_api_key}\n")
            f.write(f"POSTGRES_HOST={postgres_host}\n")
            f.write(f"POSTGRES_PORT={postgres_port}\n")
            f.write(f"POSTGRES_USER={postgres_user}\n")
            f.write(f"POSTGRES_PASSWORD={postgres_password}\n")
            f.write(f"POSTGRES_DB={postgres_db}\n")
        
        console.print("[bold green].env file created successfully![/bold green]")
        
        # Reload environment
        load_dotenv()

# Check and create .env if needed before loading
check_and_create_env()

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Postgres
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")


# Max number of characters to display in the results
LIMIT_QUERY_RESULTS = os.getenv("LIMIT_QUERY_RESULTS", 2000)
