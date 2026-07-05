import time
from groq import Groq
from app.config import settings
from app.utils.logger import logger

class GroqAPIError(Exception):
    pass

def call_groq(system_prompt: str, user_prompt: str) -> str:
    client = Groq(api_key=settings.groq_api_key)
    
    max_retries = 3
    backoff_factors = [1, 2, 4]
    
    for attempt in range(max_retries):
        try:
            start_time = time.time()
            logger.info(f"Calling Groq API (attempt {attempt + 1}/{max_retries})", extra={
                "model": settings.groq_model,
                "prompt_length": len(system_prompt) + len(user_prompt)
            })
            
            completion = client.chat.completions.create(
                model=settings.groq_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            latency = time.time() - start_time
            response_text = completion.choices[0].message.content
            
            logger.info("Groq API call succeeded", extra={
                "latency_sec": round(latency, 3),
                "response_length": len(response_text) if response_text else 0
            })
            
            return response_text
            
        except Exception as e:
            logger.warning(f"Groq API call failed on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                sleep_time = backoff_factors[attempt]
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                logger.error("Groq API call failed after max retries")
                raise GroqAPIError(f"Failed to call Groq API: {str(e)}") from e
    
    raise GroqAPIError("Unexpected error during Groq API call")
