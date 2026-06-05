from src.core.models import EnvironmentConfig, ValidationResult
from src.utils.docker_validator import DockerValidator
import structlog

logger = structlog.get_logger()

class CriticAgent:
    """
    Evaluates the generated EnvironmentConfig.
    Currently uses local dry-run validation. Could be expanded to use
    LLM-based heuristics checking.
    """
    
    def evaluate(self, config: EnvironmentConfig) -> ValidationResult:
        logger.info("CriticAgent: Evaluating via Live Sandbox...")
        
        # 1. Run strict sandbox check using Docker toolchain
        result = DockerValidator.validate(config)
        
        if not result.is_valid:
            logger.warning("CriticAgent: Sandbox failed. Returning crash logs to Generator.")
            return result
            
        # 2. Heuristic Checks (Rule-based)
        for file in config.files:
            if "docker-compose" in file.path:
                # Check for sleep infinity or similar long-running command for dev containers
                if "command:" not in file.content and "tty: true" not in file.content and "devcontainer" in file.path:
                    logger.warning("CriticAgent: Detected potential devcontainer issue (no command/tty).")
                    # It's a warning, not necessarily a hard fail, but for self-healing we could fail it
                    # return ValidationResult(is_valid=False, errors="DevContainer docker-compose.yml missing 'command: sleep infinity' or 'tty: true'. Container will exit immediately.")
                    
        return ValidationResult(is_valid=True)
