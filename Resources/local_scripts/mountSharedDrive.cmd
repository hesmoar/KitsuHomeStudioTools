@echo off
SETLOCAL


:: -----------------------------------------------------------------
:: 1. ADMINISTRATOR CHECK
:: -----------------------------------------------------------------
ECHO Checking for Administrator privileges...
net session >nul 2>&1
IF NOT ERRORLEVEL 0 (
    ECHO.
    ECHO ERROR: This setup requires Administrator privileges.
    ECHO Please right-click this file and select 'Run as administrator'.
    ECHO.
    GOTO :ErrorExit
)
ECHO Privileges OK.
ECHO.

:: 2. REGISTRY CHECK
ECHO Checking for required registry key (for drive visibility)...
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v "EnableLinkedConnections" | find "0x1" > nul

IF ERRORLEVEL 1 (
    ECHO.
    ECHO Registry key not found. This is a one-time setup.
    ECHO Adding the 'EnableLinkedConnections' key now...
    
    reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v "EnableLinkedConnections" /t REG_DWORD /d 1 /f > nul
    
    ECHO.
    ECHO -------------------- IMPORTANT ACTION REQUIRED --------------------
    ECHO.
    ECHO   The script has updated a necessary Windows setting.
    ECHO.
    ECHO   1. Please REBOOT your computer now.
    ECHO   2. After rebooting, run this setup script again.
    ECHO.
    ECHO -------------------------------------------------------------------
    ECHO.
    GOTO :ErrorExit
)
ECHO Registry key is already set. Proceeding...
ECHO.
GOTO :MountDriveLogic

:MountDriveLogic
:: --- Setup Logging ---
md "%tmp%\KitsuTaskManager" 2>nul
set LOGFILE=%tmp%\KitsuTaskManager\mountSharedgDrive.log
echo [%date% %time%] MountDriveLogic started. >> "%LOGFILE%"
ECHO.

:: --- 2. Find Google Drive Letter ---
ECHO Finding Google Drive letter...
SET "GDriveLetter="
FOR /F "tokens=2 delims==" %%d IN ('wmic volume where "Label='Google Drive'" get DriveLetter /format:list') DO (
    FOR %%G IN (%%d) DO SET "GDriveLetter=%%G"
)

IF NOT DEFINED GDriveLetter (
    ECHO ERROR: Could not find a drive with the label 'Google Drive'.
    echo [%date% %time%] ERROR: Could not find 'Google Drive' volume. >> "%LOGFILE%"
    GOTO :WorkerExit
)
ECHO Found Google Drive at: %GDriveLetter%
echo [%date% %time%] Found Google Drive at: %GDriveLetter% >> "%LOGFILE%"
ECHO.

:: --- 2. Find "My Drive" folder in correct language ---
ECHO Searching for language-specific folder (will wait for GDrive to init)...

:FindLangLoop
ECHO Checking for "Mi unidad"...
:: Use 'dir' and check the error level.
dir "%GDriveLetter%\Mi unidad" /AD >nul 2>&1
IF NOT ERRORLEVEL 1 (
    SET DriveRoot=%GDriveLetter%\Mi unidad
    GOTO :RootFound
)

ECHO Checking for "My Drive"...
dir "%GDriveLetter%\My Drive" /AD >nul 2>&1
IF NOT ERRORLEVEL 1 (
    SET DriveRoot=%GDriveLetter%\My Drive
    GOTO :RootFound
)

ECHO Folder not found yet. Google Drive may still be starting.
ECHO Waiting 10 seconds to retry...
echo [%date% %time%] Language folder not found. Retrying in 10s... >> "%LOGFILE%"
timeout /t 10 /nobreak >nul
GOTO :FindLangLoop

:RootFound
ECHO Found user's drive root: "%DriveRoot%"
echo [%date% %time%] Found user's drive root: "%DriveRoot%" >> "%LOGFILE%"
ECHO.

:: --- 3. Build the final shortcut path ---
SET "ShortcutPath=%DriveRoot%\Epic\EpicProd.lnk"
ECHO Full shortcut path set to: "%ShortcutPath%"
ECHO.


:: --- 4. Prime Google Drive ---
ECHO Priming Google Drive by finding shortcut...

:PrimeLoop
ECHO Checking for shortcut: "%ShortcutPath%"
if exist "%ShortcutPath%" (
    ECHO Shortcut file found! Attempting to "run" it to force sync...
    echo [%date% %time%] Shortcut file found. Forcing sync. >> "%LOGFILE%"
    
    pushd "%~dpShortcutPath%"
    START "" "%~nxShortcutPath%"
    popd
    
    ECHO Waiting 10 seconds for sync to complete...
    echo [%date% %time%] Priming complete. Waiting 10s for sync... >> "%LOGFILE%"
    timeout /t 10 /nobreak >nul
    
    GOTO :FindRealPath
)

ECHO Shortcut not found. Google Drive may still be starting.
ECHO Waiting 10 seconds to retry...
echo [%date% %time%] Shortcut not found. Retrying in 10s... >> "%LOGFILE%"
timeout /t 10 /nobreak >nul
GOTO :PrimeLoop

:FindRealPath
:: --- 5. Find Real Path ---
ECHO Now searching for the real folder path...
cd /d "%GDriveLetter%\.shortcut-targets-by-id"
IF ERRORLEVEL 1 (
    ECHO ERROR: Could not find %GDriveLetter%\.shortcut-targets-by-id
    echo [%date% %time%] ERROR: Could not find %GDriveLetter%\.shortcut-targets-by-id >> "%LOGFILE%"
    GOTO :WorkerExit
)

ECHO Searching for first-level sub-directory...
FOR /F "delims=" %%i IN ('dir /b /ad *') DO (
    cd "%%i"
    GOTO :Found1_Worker
)
ECHO ERROR: No sub-directories found in .shortcut-targets-by-id
ECHO This might mean the shortcut hasn't synced.
echo [%date% %time%] ERROR: No sub-directories found in .shortcut-targets-by-id >> "%LOGFILE%"
GOTO :WorkerExit

:Found1_Worker
ECHO Searching for second-level sub-directory...
FOR /F "delims=" %%j IN ('dir /b /ad *') DO (
    cd "%%j"
    GOTO :Found2_Worker
)
ECHO ERROR: No sub-directories were found inside %cd%
echo [%date% %time%] ERROR: No sub-directories found in %cd% >> "%LOGFILE%"
GOTO :WorkerExit

:Found2_Worker
SET "MyFullPath=%cd%"
ECHO Successfully captured final path: %MyFullPath%
echo [%date% %time%] Successfully found path: %MyFullPath% >> "%LOGFILE%"
ECHO.
GOTO :waitloop_Worker

:: --- 6. Share and Map ---
ECHO Now starting the folder sharing and drive sharing task...

:waitloop_Worker
if exist "%MyFullPath%" (
    echo [%date% %time%] Folder found, sharing... >> "%LOGFILE%"
    ECHO Folder found, sharing as "EPIC_PROJECT"...

    :: --- THIS IS THE FIX ---
    :: Grant permission to "everyone" (for English)
    :: We use 2>nul to hide the error if it fails (e.g., on a Spanish system)
    net share EPIC_PROJECT="%MyFullPath%" /grant:everyone,full >> "%LOGFILE%" 2>nul
    
    :: Grant permission to "Todos" (for Spanish)
    :: We use 2>nul to hide the error if it fails (e.g., on an English system)
    net share EPIC_PROJECT="%MyFullPath%" /grant:Todos,full >> "%LOGFILE%" 2>nul
    
    ::net share EPIC_PROJECT="%MyFullPath%" /grant:*S-1-1-0,full >> "%LOGFILE%" 2>&1
    
    ::IF ERRORLEVEL 1 (
    ::    ECHO ERROR: Could not share the folder. Check log for details.
    ::    echo [%date% %time%] ERROR: 'net share' command failed. >> "%LOGFILE%"
    ::    GOTO :WorkerExit
    ::)
    GOTO :mapdrive_Worker
)

ECHO ERROR: The final path %MyFullPath% does not exist.
echo [%date% %time%] ERROR: The final path %MyFullPath% does not exist. >> "%LOGFILE%"
GOTO :WorkerExit

:mapdrive_Worker
echo [%date% %time%] Mapping drive... >> "%LOGFILE%"
ECHO Deleting any old X: drive mapping...
net use X: /delete /yes >nul 2>&1

ECHO Mapping X: drive to \\localhost\EPIC_PROJECT
net use X: \\localhost\EPIC_PROJECT /persistent:yes >> "%LOGFILE%" 2>&1
    
IF ERRORLEVEL 1 (
    ECHO ERROR: Could not map the X: drive. Check log for details.
    echo [%date% %time%] ERROR: 'net use' command failed. >> "%LOGFILE%"
    GOTO :WorkerExit
)
    
echo [%date% %time%] Drive mounted, script finalized. >> "%LOGFILE%"
ECHO.
ECHO --- SCRIPT COMPLETE ---
ECHO Successfully shared and mapped the drive.
GOTO :WorkerExit

:: -----------------------------------------------------------------
:: EXIT LABELS
:: -----------------------------------------------------------------
:ErrorExit
ECHO.
ECHO --- SCRIPT ENDED WITH ERRORS (or requires reboot) ---
ECHO Press any key to exit...
pause > nul
GOTO :EOF

:End
ECHO.
ECHO Press any key to exit...
pause > nul
GOTO :EOF

:WorkerExit
:: When the worker is done, just exit
GOTO :EOF