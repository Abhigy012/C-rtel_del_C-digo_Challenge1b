#!/usr/bin/env pwsh

Write-Host "=== ADOBE HACKATHON - ROUND 1B: PERSONA-DRIVEN INTELLIGENCE ===" -ForegroundColor Green
Write-Host ""

# Check for challenge1b_input.json
$inputJsonExists = Test-Path "input_1b/challenge1b_input.json"
if (-not $inputJsonExists) {
    Write-Host "⚠️  No challenge1b_input.json found in input_1b directory!" -ForegroundColor Yellow
    Write-Host "Please add challenge1b_input.json file and try again."
    exit 1
}

# Check for PDFs directory
$pdfsDirExists = Test-Path "input_1b/PDFs"
if (-not $pdfsDirExists) {
    Write-Host "⚠️  No PDFs directory found in input_1b!" -ForegroundColor Yellow
    Write-Host "Please create input_1b/PDFs directory and add PDF files."
    exit 1
}

# Check if PDFs directory has files
$pdfCount = (Get-ChildItem -Path "input_1b/PDFs" -Filter "*.pdf" -ErrorAction SilentlyContinue).Count
if ($pdfCount -eq 0) {
    Write-Host "⚠️  No PDF files found in input_1b/PDFs directory!" -ForegroundColor Yellow
    Write-Host "Please add PDF files to input_1b/PDFs folder and try again."
    exit 1
}

Write-Host "📄 Found $pdfCount PDF files in input_1b/PDFs directory" -ForegroundColor Cyan
Write-Host "📋 Found challenge1b_input.json configuration" -ForegroundColor Cyan
Write-Host "🧹 Output directory will be cleaned automatically"
Write-Host "🚀 Starting Round 1B processing..."
Write-Host ""

# Build Docker image
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
docker build --no-cache --platform linux/amd64 -t challenge1b:latest .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}

# Run Docker container
Write-Host "🏃 Running Challenge 1B..." -ForegroundColor Yellow
docker run --rm `
    -v "${PWD}/input_1b:/app/input_1b" `
    -v "${PWD}/output_1b:/app/output_1b" `
    --network none `
    challenge1b:latest python src/extract_intel.py

Write-Host ""
Write-Host "✅ Round 1B completed!" -ForegroundColor Green
Write-Host "📁 Check output_1b folder for results"

# Show output files
$outputExists = Test-Path "output_1b/challenge1b_output.json"
if ($outputExists) {
    Write-Host "Generated challenge1b_output.json successfully" -ForegroundColor Cyan
}
