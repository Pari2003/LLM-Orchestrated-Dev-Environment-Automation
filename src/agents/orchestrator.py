from src.agents.generator import GeneratorAgent
from src.agents.critic import CriticAgent
from src.utils.file_writer import FileWriter
from src.core.models import EnvironmentConfig
import structlog

logger = structlog.get_logger()

class OrchestratorAgent:
    """
    Manages the self-healing loop between the Generator and the Critic.
    """
    
    def __init__(self, max_iterations: int = 3):
        self.generator = GeneratorAgent()
        self.critic = CriticAgent()
        self.max_iterations = max_iterations
        
    def run(self, prompt: str, target_dir: str = ".") -> EnvironmentConfig:
        logger.info("OrchestratorAgent: Starting generation process.", target_dir=target_dir)
        
        previous_errors = None
        final_config = None
        
        for i in range(self.max_iterations):
            logger.info(f"OrchestratorAgent: Iteration {i+1}/{self.max_iterations}")
            
            # Generate config
            config = self.generator.generate(prompt, previous_errors)
            
            # Evaluate config
            validation = self.critic.evaluate(config)
            
            if validation.is_valid:
                logger.info("OrchestratorAgent: Configuration validated successfully. Writing to disk.")
                final_config = config
                break
            else:
                logger.warning("OrchestratorAgent: Configuration failed validation.", errors=validation.errors)
                previous_errors = validation.errors
                
        if not final_config:
            logger.error("OrchestratorAgent: Failed to generate a valid configuration after max iterations. Saving last attempt anyway.")
            final_config = config # Save the best we have
            
        # Write files
        FileWriter.write_environment(final_config, target_dir)
        return final_config
