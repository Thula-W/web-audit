from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from .models import AuditRequest, AuditResponse
from .scraper import get_metrics
from .ai_analyzer import analyze

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Website Audit Tool",
    description="AI-powered website audit tool for single URLs",
    version="1.0.0"
)


@app.post("/audit", response_model=AuditResponse)
async def audit(request: AuditRequest):
    """
    Audit a single webpage for SEO, messaging, CTAs, content, and UX.
    
    Returns:
    - Factual metrics (word count, headings, CTAs, links, images, meta)
    - AI insights (SEO, messaging, CTA, content, UX)
    - Actionable recommendations (3-5 items)
    - Prompt logs for transparency
    """
    try:
        # Validate URL
        if not request.url.startswith(('http://', 'https://')):
            raise ValueError("URL must start with http:// or https://")
        
        # Extract metrics
        metrics = get_metrics(request.url)
        
        # Get AI insights
        insights, recommendations, logs = analyze(metrics)
        
        return {
            "metrics": metrics,
            "insights": insights,
            "recommendations": recommendations,
            "prompt_logs": logs
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid URL: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
