#!/usr/bin/env python3
"""
AI Roast Master - Launch Script
Run this to start the application
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

if __name__ == "__main__":
    try:
        import uvicorn
        from api import app
        
        print("Starting AI Roast Master...")
        print("Open your browser to: http://localhost:8001")
        print("Press Ctrl+C to stop")
        
        os.chdir(backend_path)
        uvicorn.run("api:app", host="127.0.0.1", port=8001, reload=True)
        
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
    except Exception as e:
        print(f"Error starting server: {e}")
