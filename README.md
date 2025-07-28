# Adobe Hackathon - Challenge 1B: Persona-Driven Intelligence

## Overview
This challenge extracts relevant content from PDFs based on a specific persona and job description using advanced ML techniques.

## Project Structure
```
challenge1b/
├── input_1b/          # Input configuration and PDFs
│   ├── challenge1b_input.json    # Configuration file
│   └── PDFs/          # PDF documents to process
├── output_1b/         # JSON outputs (auto-cleaned)
├── src/               # Python source code
│   └── extract_intel.py
├── run_1b.ps1         # PowerShell script to run the challenge
├── requirements.txt   # Python dependencies
├── Dockerfile         # Docker configuration
└── README.md         # This file
```

## Quick Start

### Prerequisites
- Docker installed on your system
- PowerShell (already available on Windows)

### Steps to Run

1. **Navigate to the project directory:**
   ```bash
   cd challenge1b
   ```

2. **Build the Docker image:**
   ```bash
   docker build --no-cache --platform linux/amd64 -t challenge1b:latest .
   ```

3. **Run Challenge 1B:**
   ```bash
   docker run --rm -v "$(pwd)/input_1b:/app/input_1b" -v "$(pwd)/output_1b:/app/output_1b" --network none challenge1b:latest
   ```

### Alternative: Using PowerShell Script
```powershell
.\run_1b.ps1
```

## Current Configuration
- **Persona**: Travel Planner
- **Job**: Plan a trip of 4 days for a group of 10 college friends
- **Documents**: 7 South of France travel guide PDFs

## Input/Output
- **Input**: 
  - `challenge1b_input.json` (persona and job configuration)
  - PDF files in `input_1b/PDFs/` directory
- **Output**: `challenge1b_output.json` with ranked sections and refined subsections

## Technology Stack
- TF-IDF vectorization with cosine similarity
- scikit-learn for machine learning operations
- PyPDF2 & pdfplumber for PDF text extraction
- Docker for containerized execution

## Features
- Processes multiple PDFs simultaneously
- Ranks document sections by relevance to persona+job combination
- Extracts and refines subsections with relevance scores
- Auto-cleans output directory before each run
- Supports different personas and job descriptions
