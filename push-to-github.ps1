# 🚀 Quick GitHub Push Script

# This script will help you push your RAG Chatbot to GitHub
# Run this in PowerShell from the RAG_chatbot directory

Write-Host "🚀 RAG Chatbot - GitHub Push Setup" -ForegroundColor Cyan
Write-Host "===================================`n" -ForegroundColor Cyan

# Step 1: Initialize Git
Write-Host "Step 1: Initializing Git repository..." -ForegroundColor Yellow
git init

# Step 2: Configure Git (Update with your details)
Write-Host "`nStep 2: Configuring Git user..." -ForegroundColor Yellow
Write-Host "Enter your name:" -ForegroundColor Green
$userName = Read-Host
git config user.name "$userName"

Write-Host "Enter your email:" -ForegroundColor Green
$userEmail = Read-Host
git config user.email "$userEmail"

# Step 3: Verify .env is not tracked
Write-Host "`nStep 3: Verifying .env security..." -ForegroundColor Yellow
if (git check-ignore .env) {
    Write-Host "✅ .env file is properly ignored" -ForegroundColor Green
} else {
    Write-Host "⚠️  WARNING: .env might not be ignored properly!" -ForegroundColor Red
}

# Step 4: Stage all files
Write-Host "`nStep 4: Staging files..." -ForegroundColor Yellow
git add .

# Show what will be committed
Write-Host "`nFiles to be committed:" -ForegroundColor Cyan
git status --short

# Step 5: Verify critical files are ignored
Write-Host "`nStep 5: Security check..." -ForegroundColor Yellow
$envTracked = git ls-files | Select-String -Pattern "\.env$" -Quiet
$uploadsTracked = git ls-files | Select-String -Pattern "uploads/" -Quiet

if ($envTracked) {
    Write-Host "❌ ERROR: .env file is tracked! Aborting." -ForegroundColor Red
    Write-Host "Run: git rm --cached .env" -ForegroundColor Yellow
    exit 1
}

if ($uploadsTracked) {
    Write-Host "⚠️  WARNING: Upload files are tracked!" -ForegroundColor Red
}

Write-Host "✅ Security check passed" -ForegroundColor Green

# Step 6: Create initial commit
Write-Host "`nStep 6: Creating initial commit..." -ForegroundColor Yellow
git commit -m "🎉 Initial commit: Production-ready RAG Chatbot with multi-chat persistence"

# Step 7: Instructions for GitHub
Write-Host "`n✅ Local repository ready!" -ForegroundColor Green
Write-Host "`n📋 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Go to https://github.com/new" -ForegroundColor White
Write-Host "2. Create a new repository named: RAG-Chatbot" -ForegroundColor White
Write-Host "3. Do NOT initialize with README, .gitignore, or license" -ForegroundColor White
Write-Host "4. Copy the repository URL" -ForegroundColor White
Write-Host "5. Run these commands (replace YOUR_USERNAME):`n" -ForegroundColor White

Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/RAG-Chatbot.git" -ForegroundColor Yellow
Write-Host "   git branch -M main" -ForegroundColor Yellow
Write-Host "   git push -u origin main" -ForegroundColor Yellow

Write-Host "`n🎉 Your RAG Chatbot will be live on GitHub!" -ForegroundColor Green
Write-Host "📸 Don't forget to add screenshots to docs/screenshots/" -ForegroundColor Magenta
