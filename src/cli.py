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
    
    target_dir = "generated_env"
    
    with console.status("[bold green]Architect Agent designing architecture...[/bold green]", spinner="dots") as status:
        orchestrator = OrchestratorAgent()
        
        status.update("[bold cyan]Orchestrator looping with Critic and Live Sandbox...[/bold cyan]")
        config = orchestrator.run(prompt, target_dir)
    
    console.print(f"[bold green]✅ Done! Environment is ready and verified in '{target_dir}'.[/bold green]")
    console.print("[yellow]Post-create instructions:[/yellow]")
    console.print(config.post_create_instructions)

if __name__ == '__main__':
    main()
