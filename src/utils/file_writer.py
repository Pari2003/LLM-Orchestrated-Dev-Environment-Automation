import os
from pathlib import Path
from src.core.models import EnvironmentConfig
import structlog

logger = structlog.get_logger()

class FileWriter:
    """
    Safely writes the generated files to the target directory.
    """
    
    @staticmethod
    def write_environment(config: EnvironmentConfig, target_dir: str = "."):
        base_path = Path(target_dir)
        
        logger.info("FileWriter: Writing files to disk...", target_dir=target_dir)
        
        for file in config.files:
            file_path = base_path / file.path
            
            # Ensure parent directories exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file.content)
                
            if file.is_executable:
                # Make file executable on Unix-like systems
                try:
                    os.chmod(file_path, 0o755)
                except Exception as e:
                    logger.warning("Could not set executable permission", path=file.path, error=str(e))
                    
            logger.debug("Wrote file", path=file.path)
            
        logger.info("FileWriter: Successfully wrote all files.", count=len(config.files))
