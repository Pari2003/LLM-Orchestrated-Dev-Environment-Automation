from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class FileContent(BaseModel):
    path: str = Field(..., description="The relative path to the file, e.g., 'docker-compose.yml' or '.devcontainer/devcontainer.json'")
    content: str = Field(..., description="The full, raw text content of the file. Do not use markdown backticks.")
    is_executable: bool = Field(default=False, description="Whether the file needs execution permissions (e.g., init scripts)")

class EnvironmentConfig(BaseModel):
    services: List[str] = Field(..., description="List of services identified (e.g., ['node_app', 'postgres', 'redis'])")
    files: List[FileContent] = Field(..., description="The complete set of files needed for the environment")
    post_create_instructions: str = Field(..., description="Brief instructions on how to start the environment (e.g., 'docker-compose up -d')")
    
class ValidationResult(BaseModel):
    is_valid: bool
    errors: Optional[str] = None
