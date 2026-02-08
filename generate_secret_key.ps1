# Generate Strong SECRET_KEY for Production
# Run this script: .\generate_secret_key.ps1

Write-Host "Generating strong SECRET_KEY..." -ForegroundColor Cyan

# Generate using Python
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

Write-Host "`nCopy the SECRET_KEY above and update it in your .env file" -ForegroundColor Green
Write-Host "NEVER commit the .env file to version control!" -ForegroundColor Yellow
