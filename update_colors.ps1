# Color Scheme Update Script
# Changes entire app from blue to matte gold & black

# Color Mappings:
# Old Blue -> New Gold/Black
# #0078d4 (primary blue) -> #C9A961 (matte gold)
# #106ebe (dark blue) -> #B8954D (dark gold)
# #005a9e (darker blue) -> #B8954D (dark gold)
# white backgrounds -> #222222 (matte black cards)
# #faf9f8, #f3f2f1 (light grays) -> #1a1a1a (matte black)
# #323130 (dark text) -> #e8e8e8 (light text for dark bg)
# #605e5c (secondary text) -> #b8b8b8 (secondary light text)

$files = Get-ChildItem -Path "templates" -Filter "*.html" -Recurse

Write-Host "🎨 Updating color scheme to Matte Gold & Black..." -ForegroundColor Cyan
Write-Host ""

$replacements = @{
    '#0078d4' = '#C9A961';
    '#106ebe' = '#B8954D';
    '#005a9e' = '#B8954D';
    '#0086f0' = '#D4B76E';
    'background: white;' = 'background: #222222;';
    'background-color: white;' = 'background-color: #222222;';
    '#faf9f8' = '#0f0f0f';
    '#f3f2f1' = '#1a1a1a';
    '#edebe9' = '#3a3a3a';
    '#323130' = '#e8e8e8';
    '#605e5c' = '#b8b8b8';
    '#8a8886' = '#888888';
    '#a19f9d' = '#888888';
    '#107c10' = '#4CAF50';
    '#a80000' = '#f44336';
    '#a4262c' = '#f44336';
    '#d83b01' = '#C9A961'
}

$count = 0
foreach ($file in $files) {
    $content = Get-Content $file.FullName -Raw -ErrorAction SilentlyContinue
    if ($null -eq $content) { continue }
    
    $modified = $false
    foreach ($old in $replacements.Keys) {
        $new = $replacements[$old]
        if ($content -match [regex]::Escape($old)) {
            $content = $content -replace [regex]::Escape($old), $new
            $modified = $true
        }
    }
    
    if ($modified) {
        Set-Content -Path $file.FullName -Value $content -NoNewline
        $count++
        Write-Host "✓ Updated: $($file.Name)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "✅ Color scheme update complete!" -ForegroundColor Green
Write-Host "📊 Files modified: $count" -ForegroundColor Yellow
Write-Host ""
Write-Host "🎨 Color Palette:" -ForegroundColor Cyan
Write-Host "   Primary: Matte Gold #C9A961" -ForegroundColor Yellow
Write-Host "   Background: Matte Black #0f0f0f" -ForegroundColor White
Write-Host "   Cards: Dark #222222" -ForegroundColor Gray
Write-Host "   Text: Light #e8e8e8" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Restart Flask server to see changes!" -ForegroundColor Cyan
