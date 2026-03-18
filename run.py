#!/usr/bin/env python
"""
Entry point for running the Website Audit Tool API.

Usage:
    python run.py
    
The API will be available at http://localhost:8000
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Verify API key is set
if not os.getenv('OPENAI_API_KEY'):
    print("ERROR: OPENAI_API_KEY environment variable not set")
    print("Please create a .env file with your OpenAI API key:")
    print("  OPENAI_API_KEY=your_api_key_here")
    sys.exit(1)

if __name__ == "__main__":
    print("Starting Website Audit Tool API...")
    print("API available at: http://localhost:8000")
    print("Docs available at: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
