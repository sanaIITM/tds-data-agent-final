#!/usr/bin/env python3
"""
TDS Data Analyst Agent - Entry Point
Single command deployment for Render
"""

import os
import uvicorn
from app import app

if __name__ == "__main__":
    # Get port from environment (Render sets this)
    port = int(os.environ.get("PORT", 8000))
    
    # Run with uvicorn
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        log_level="info"
    )
