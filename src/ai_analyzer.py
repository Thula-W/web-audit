import httpx
import openai
import os
import json
import datetime
from pathlib import Path
from .prompts import ANALYSER_SYSTEM_PROMPT

def analyze(metrics: dict) -> tuple:
    """
    Analyze extracted metrics using OpenAI GPT-4o-mini and generate insights.
    
    Args:
        metrics: Dictionary of extracted factual metrics from the webpage
        
    Returns:
        Tuple of (insights dict, recommendations list, prompt_logs dict)
    """
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise Exception("OPENAI_API_KEY environment variable not set")
    
    http_client = httpx.Client(
        trust_env=False 
    )
    client = openai.OpenAI(api_key=api_key, http_client=http_client)

    user_prompt = f"Factual metrics extracted from the webpage:\n{json.dumps(metrics, indent=2)}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": ANALYSER_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.5,
            max_tokens=1500
        )
        raw_output = response.choices[0].message.content
        
        # Parse JSON from response
        result = json.loads(raw_output.strip())
        insights = result.get('insights', {})
        recommendations = result.get('recommendations', [])
        
        # Prepare prompt logs
        logs = {
            "timestamp": datetime.datetime.now().isoformat(),
            "system_prompt": ANALYSER_SYSTEM_PROMPT,
            "user_prompt": user_prompt,
            "raw_output": raw_output,
            "parsed_insights": insights,
            "parsed_recommendations": recommendations
        }
        
        # Save logs
        prompts_dir = Path(__file__).parent.parent / 'logs'
        prompts_dir.mkdir(exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        log_file = prompts_dir / f"{timestamp}.json"
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
        
        return insights, recommendations, logs
    except json.JSONDecodeError as e:
        raise Exception(f"Failed to parse AI response as JSON: {str(e)}")
    except Exception as e:
        raise Exception(f"Error in AI analysis: {str(e)}")
