import subprocess
import tempfile
import os
from pathlib import Path
from src.core.models import EnvironmentConfig, ValidationResult
from src.utils.file_writer import FileWriter
import structlog

logger = structlog.get_logger()

class DockerValidator:
    """
    Validates Docker and DevContainer configurations by performing a dry-run
    using actual local Docker tools.
    """
    
    @staticmethod
    def validate(config: EnvironmentConfig) -> ValidationResult:
        """
        Writes the config to a temp directory and runs `docker-compose config`
        to check for syntax and reference errors.
        """
        logger.info("DockerValidator: Running dry-run validation...")
        
        # Check if there's a docker-compose file
        has_compose = any(f.path.endswith("docker-compose.yml") or f.path.endswith("docker-compose.yaml") for f in config.files)
        
        if not has_compose:
            return ValidationResult(is_valid=True) # Nothing to validate via compose
            
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write files to temp dir
            FileWriter.write_environment(config, target_dir=temp_dir)
            
            # Find the compose file path (could be in .devcontainer or root)
            compose_path = None
            for f in config.files:
                if f.path.endswith("docker-compose.yml") or f.path.endswith("docker-compose.yaml"):
                    compose_path = os.path.join(temp_dir, f.path)
                    break
                    
            if not compose_path:
                return ValidationResult(is_valid=True)
                
            try:
                # Run docker-compose config (dry run)
                result = subprocess.run(
                    ["docker-compose", "-f", compose_path, "config"],
                    capture_output=True,
                    text=True,
                    cwd=temp_dir
                )
                
                if result.returncode == 0:
                    logger.info("DockerValidator: Validation passed.")
                    return ValidationResult(is_valid=True)
                else:
                    logger.warning("DockerValidator: Validation failed.", error=result.stderr)
                    return ValidationResult(
                        is_valid=False, 
                        errors=f"Docker Compose syntax error:\n{result.stderr}\n\nPlease fix the docker-compose.yml file."
                    )
            except FileNotFoundError:
                logger.warning("DockerValidator: docker-compose not found on host. Skipping strict validation.")
                return ValidationResult(is_valid=True)
            except Exception as e:
                logger.error("DockerValidator: Unexpected error during validation.", error=str(e))
                return ValidationResult(is_valid=False, errors=str(e))
