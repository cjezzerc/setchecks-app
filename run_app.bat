@echo off

REM Usage: e.g.      .\run_app.bat 311 john-smith-author 89abcdef-9876-0123-4567-89abcdef

REM Run pip install every time as quicker than trying to document why run it once
REM The python version is entered as first argument (e.g. 310 if installed verion to use is v3.10)
C:%HOMEPATH%\AppData\Local\Programs\Python\Python%1\scripts\pip install -r requirements.txt

REM routes to the dev server and its sauthorisation server
set ONTOSERVER_INSTANCE=https://dev.ontology.nhs.uk/dev1/fhir/
set ONTOAUTH_INSTANCE=https://dev.ontology.nhs.uk/authorisation/auth/realms/terminology/protocol/openid-connect/token

REM Enter these as second and third arguments
set ONTOSERVER_USERNAME=%2
set ONTOSERVER_SECRET=%3

REM Start the app
echo Executing C:%HOMEPATH%\AppData\Local\Programs\Python\Python%1\python run_app.py
C:%HOMEPATH%\AppData\Local\Programs\Python\Python%1\python run_app.py

REM To stop the app type Ctrl-c  
REM A prompt "Terminate batch job (Y/N)?" should come up)