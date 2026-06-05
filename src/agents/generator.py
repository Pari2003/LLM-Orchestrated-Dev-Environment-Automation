from src.core.models import EnvironmentConfig
from src.llm.provider import generate_structured
import structlog

logger = structlog.get_logger()

class GeneratorAgent:
    """
    Generates the complete set of files and configuration for a dev environment
    based on a user prompt and optional feedback from the Critic.
    """
    
    SYSTEM_PROMPT = """You are an expert DevOps and Platform Engineer. 
Your task is to design a complete, multi-container development environment based on the user's request.
You MUST output a valid JSON matching the EnvironmentConfig schema.

Best Practices you MUST follow:
1. Include a .devcontainer/devcontainer.json file if applicable, with appropriate VS Code extensions.
2. In docker-compose.yml, development services should often use `command: sleep infinity` or a dev server with hot-reloading so the container doesn't exit immediately.
3. Always include a Dockerfile if custom dependencies are needed.
4. Provide clear post_create_instructions (e.g., 'docker-compose up -d').
5. Create necessary configuration files (e.g. initial schema.sql for Postgres).
"""

    def generate(self, user_prompt: str, previous_errors: str = None) -> EnvironmentConfig:
        logger.info("GeneratorAgent: Designing architecture...", prompt=user_prompt)
        
        prompt = user_prompt
        if previous_errors:
            prompt += f"\n\nIMPORTANT: Your previous attempt had the following errors. Please fix them:\n{previous_errors}"
            
        env_config: EnvironmentConfig = generate_structured(
            model_class=EnvironmentConfig,
            system_prompt=self.SYSTEM_PROMPT,
            user_prompt=prompt
        )
        
        logger.info("GeneratorAgent: Generated environment config.", services=env_config.services, files_count=len(env_config.files))
        return env_config
