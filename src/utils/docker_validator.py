import subprocess
import tempfile
import os
import time
from typing import List, Dict
from src.core.models import EnvironmentConfig, ValidationResult
from src.utils.file_writer import FileWriter
import structlog

logger = structlog.get_logger()

class DockerValidator:
    """
    Validates Docker configurations by running a Live Sandbox test.
    It boots the environment, checks for immediate container crashes, 
    extracts crash logs, and tears it down.
    """
    
    @staticmethod
    def validate(config: EnvironmentConfig) -> ValidationResult:
        logger.info("DockerValidator: Starting Live Sandbox Validation...")
        
        has_compose = any(f.path.endswith("docker-compose.yml") or f.path.endswith("docker-compose.yaml") for f in config.files)
        
        if not has_compose:
            logger.info("DockerValidator: No docker-compose.yml found. Skipping sandbox test.")
            return ValidationResult(is_valid=True)
            
        with tempfile.TemporaryDirectory() as temp_dir:
            FileWriter.write_environment(config, target_dir=temp_dir)
            
            compose_path = next((os.path.join(temp_dir, f.path) for f in config.files if "docker-compose" in f.path), None)
            
            if not compose_path:
                return ValidationResult(is_valid=True)
                
            try:
                # Step 1: Syntax / Config Check
                config_result = subprocess.run(
                    ["docker-compose", "-f", compose_path, "config"],
                    capture_output=True, text=True, cwd=temp_dir
                )
                if config_result.returncode != 0:
                    return ValidationResult(is_valid=False, errors=f"Syntax Error:\n{config_result.stderr}")

                # Step 2: Boot Sandbox
                logger.info("DockerValidator: Syntax valid. Booting Sandbox containers...")
                up_result = subprocess.run(
                    ["docker-compose", "-f", compose_path, "up", "-d", "--build"],
                    capture_output=True, text=True, cwd=temp_dir
                )
                if up_result.returncode != 0:
                    return ValidationResult(is_valid=False, errors=f"Build/Boot Error:\n{up_result.stderr}")
                    
                # Step 3: Monitor for 5 seconds
                logger.info("DockerValidator: Containers running. Monitoring for 5 seconds...")
                time.sleep(5)
                
                # Step 4: Check for crashed containers
                ps_result = subprocess.run(
                    ["docker-compose", "-f", compose_path, "ps", "--format", "json"],
                    capture_output=True, text=True, cwd=temp_dir
                )
                
                # Simple string check for "Exit" or "exited" state in ps output
                # docker-compose ps --format json differs slightly across versions, so we use string parsing
                ps_output = ps_result.stdout.lower()
                if "exit" in ps_output or "restarting" in ps_output:
                    # A container crashed. Let's get the logs.
                    logger.warning("DockerValidator: Detected crashed container. Extracting logs...")
                    logs_result = subprocess.run(
                        ["docker-compose", "-f", compose_path, "logs", "--tail=50"],
                        capture_output=True, text=True, cwd=temp_dir
                    )
                    
                    error_msg = (
                        "Sandbox Test Failed! One or more containers crashed immediately after booting.\n"
                        f"Here are the recent container logs:\n{logs_result.stdout}\n"
                        "Please analyze the stack trace/error logs and update the Dockerfile or docker-compose.yml to fix this."
                    )
                    return ValidationResult(is_valid=False, errors=error_msg)
                
                logger.info("DockerValidator: Live Sandbox Test Passed! No containers crashed.")
                return ValidationResult(is_valid=True)
                
            except FileNotFoundError:
                logger.warning("DockerValidator: docker-compose not found. Skipping live test.")
                return ValidationResult(is_valid=True)
            except Exception as e:
                logger.error("DockerValidator: Unexpected error.", error=str(e))
                return ValidationResult(is_valid=False, errors=str(e))
            finally:
                # Step 5: Tear Down
                logger.info("DockerValidator: Tearing down Sandbox...")
                subprocess.run(
                    ["docker-compose", "-f", compose_path, "down", "-v", "--remove-orphans"],
                    capture_output=True, cwd=temp_dir
                )
