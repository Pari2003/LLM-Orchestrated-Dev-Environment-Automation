import instructor
from litellm import completion
from src.core.config import settings

def get_llm_client():
    """
    Returns an instructor-patched LiteLLM client for structured data extraction.
    We use litellm.completion as the base, which instructor can wrap.
    However, instructor primarily wraps the standard openai.OpenAI client.
    Since litellm can be drop-in replaced or we can just use the OpenAI client
    pointing to Ollama's local endpoint.
    """
    import openai
    
    # If using local Ollama, point OpenAI client to Ollama's API base
    client = openai.OpenAI(
        base_url=f"{settings.api_base}/v1", 
        api_key="ollama" # api key is required by the client but ignored by ollama
    )
    
    # Patch the client with instructor
    # For local llama3.2, mode=instructor.Mode.JSON is generally best if tool calling isn't perfectly supported
    patched_client = instructor.from_openai(client, mode=instructor.Mode.JSON)
    return patched_client

def generate_structured(model_class, system_prompt: str, user_prompt: str):
    """
    Generate a Pydantic model response using the configured LLM.
    """
    client = get_llm_client()
    
    response = client.chat.completions.create(
        model=settings.llm_model.replace("ollama/", ""), # instructor/openai client just needs the model name
        response_model=model_class,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_retries=settings.max_retries
    )
    return response
