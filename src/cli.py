import click
from rich.console import Console
from rich.panel import Panel
import asyncio

console = Console()

@click.group()
def main():
    """LLM-Orchestrated Dev Environment Automation"""
    pass

@main.command()
@click.argument('prompt', type=str)
def generate(prompt):
    """Generate a development environment from a natural language prompt."""
    console.print(Panel(f"Generating dev environment for: [bold cyan]{prompt}[/bold cyan]", title="AI Architect"))
    
    from src.agents.orchestrator import OrchestratorAgent
    
    # We create a target directory based on the prompt or just use current dir.
    # For now, let's create a folder named 'generated_env'
    target_dir = "generated_env"
    
    orchestrator = OrchestratorAgent()
    config = orchestrator.run(prompt, target_dir)
    
    console.print(f"[green]Done! Environment is ready in '{target_dir}'.[/green]")
    console.print("[yellow]Post-create instructions:[/yellow]")
    console.print(config.post_create_instructions)

if __name__ == '__main__':
    main()
