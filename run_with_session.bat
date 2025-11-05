@echo off
echo ====================================================
echo LINKEDIN SCRAPER WITH SESSION MANAGEMENT
echo ====================================================

echo Checking for saved session...
if exist linkedin_auth.json (
    echo Saved session found!
    echo Starting scraper with saved session...
    python use_saved_session.py
) else (
    echo No saved session found.
    echo Please run manual_login_and_save.py first to create a session.
    echo Opening manual login script...
    python manual_login_and_save.py
)

pause