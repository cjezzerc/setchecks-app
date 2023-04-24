@echo off

REM This is a convenience script while checking installations running under pure Windows
REM For regular usage use the other script run_app.bat

REM This version assumes running in a venv (for testing)

REM Usage: e.g.      run_app.bat john-smith-author 89abcdef-9876-0123-4567-89abcdef

REM This venv version does NOT run pip install by default

REM routes to the dev server and its sauthorisation server
set ONTOSERVER_INSTANCE=https://dev.ontology.nhs.uk/dev1/fhir/
set ONTOAUTH_INSTANCE=https://dev.ontology.nhs.uk/authorisation/auth/realms/terminology/protocol/openid-connect/token

REM Enter these as first and second arguments
set ONTOSERVER_USERNAME=%1
set ONTOSERVER_SECRET=%2

REM Start the app
python run_app.py
