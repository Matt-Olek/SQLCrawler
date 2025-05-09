from agent import graph
from db_utility import PostgresDB
from rich.console import Console
from rich.markdown import Markdown
from config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
import pyfiglet
import time
console = Console()

print("\n")
print(pyfiglet.figlet_format("SQL Crawler"))

# Configuration explanation
config = {"configurable": {"thread_id": "1"}}
console.print("[bold yellow]Configuration:[/bold yellow]")
console.print(f"- Postgres Host: {POSTGRES_HOST}")
console.print(f"- Postgres Port: {POSTGRES_PORT}")
console.print(f"- Postgres User: {POSTGRES_USER}")
console.print(f"- Postgres Password: {POSTGRES_PASSWORD}")
console.print(f"- Postgres DB: {POSTGRES_DB}")
console.print()

# BD Health Check
db = PostgresDB()
if db.health_check():
    console.print("[bold green]Database:[/bold green] Connected")
else:
    console.print("[bold red]Database:[/bold red] Failed to connect - See src/config.py")
    exit()


console.print()
def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}, config=config):
        for value in event.values():
            if not hasattr(value["messages"][-1], "tool_call_id"):
                if len(value["messages"][-1].content) > 0:
                    console.print("[bold blue]Assistant:[/bold blue]", Markdown(value["messages"][-1].content))
            else:
                console.print("[bold violet]Tool:[/bold violet]", Markdown("Executing SQL query"))


while True:
    try:
        console.print("[bold green]User:[/bold green] ", end="")
        user_input = input()
        if user_input.lower() in ["quit", "exit", "q"]:
            console.print("[yellow]Goodbye![/yellow]")
            break
        stream_graph_updates(user_input)
    except:
        break