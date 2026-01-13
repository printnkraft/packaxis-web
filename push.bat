@echo off
setlocal enabledelayedexpansion

cd /d "C:\Users\pujan\OneDrive\Desktop\packaxis web"

git config user.email "admin@packaxis.ca"
git config user.name "PackAxis Admin"

git push -u origin main --force

echo Push completed. Press any key to close.
pause
