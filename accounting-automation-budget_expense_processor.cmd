
@echo off
:loop
REM Your command goes here
echo Running task at %time%

cd C:\xampp\htdocs\acconuting-automation
cscript .\budget_expense_processor.vbs
php.exe .\budget_expense_post-processor.php

REM Wait for 1800 seconds (30 minutes)
timeout /t 1800 /nobreak

goto loop


