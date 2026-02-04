# EFT Payment with Proof of Payment - Quick Setup Guide

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  EFT/POP System Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Install Python packages
Write-Host "[1/4] Installing Python packages..." -ForegroundColor Yellow
pip install pytesseract PyPDF2 pdf2image

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Python packages installed successfully" -ForegroundColor Green
} else {
    Write-Host "✗ Error installing Python packages" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Create upload directory
Write-Host "[2/4] Creating upload directory..." -ForegroundColor Yellow
$uploadPath = "static\uploads\proof_of_payments"
if (!(Test-Path $uploadPath)) {
    New-Item -ItemType Directory -Path $uploadPath -Force | Out-Null
    Write-Host "✓ Upload directory created: $uploadPath" -ForegroundColor Green
} else {
    Write-Host "✓ Upload directory already exists" -ForegroundColor Green
}
Write-Host ""

# Step 3: Database migration
Write-Host "[3/4] Creating database migration..." -ForegroundColor Yellow
Write-Host "Running: flask db migrate -m 'Add ProofOfPayment model'" -ForegroundColor Gray
flask db migrate -m "Add ProofOfPayment model for EFT verification"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Migration created successfully" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "Running: flask db upgrade" -ForegroundColor Gray
    flask db upgrade
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Database upgraded successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Error upgrading database" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✗ Error creating migration" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 4: Tesseract OCR check
Write-Host "[4/4] Checking Tesseract OCR..." -ForegroundColor Yellow

$tesseractPaths = @(
    "C:\Program Files\Tesseract-OCR\tesseract.exe",
    "C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    "$env:LOCALAPPDATA\Programs\Tesseract-OCR\tesseract.exe"
)

$tesseractFound = $false
foreach ($path in $tesseractPaths) {
    if (Test-Path $path) {
        Write-Host "✓ Tesseract OCR found at: $path" -ForegroundColor Green
        $tesseractFound = $true
        break
    }
}

if (!$tesseractFound) {
    Write-Host "⚠ Tesseract OCR not found!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please install Tesseract OCR:" -ForegroundColor Yellow
    Write-Host "  Option 1: Download from https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor White
    Write-Host "  Option 2: Install via Chocolatey: choco install tesseract" -ForegroundColor White
    Write-Host ""
    Write-Host "After installation, update ocr_service.py line 9 with the correct path." -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "NOTE: If Tesseract is not in the default location, update ocr_service.py line 9" -ForegroundColor Yellow
}
Write-Host ""

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor White
Write-Host "1. ✓ Python packages installed" -ForegroundColor Green
Write-Host "2. ✓ Upload directory created" -ForegroundColor Green
Write-Host "3. ✓ Database migration applied" -ForegroundColor Green

if ($tesseractFound) {
    Write-Host "4. ✓ Tesseract OCR ready" -ForegroundColor Green
} else {
    Write-Host "4. ⚠ Install Tesseract OCR (see above)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "You can now test the EFT payment with proof of payment upload!" -ForegroundColor Green
Write-Host "See EFT_POP_IMPLEMENTATION.md for full documentation." -ForegroundColor White
Write-Host ""
