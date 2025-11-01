@echo off
set LOGFILE=%tmp%\KitsuTaskManager\mountSharedgDrive.log
echo [%date% %time%] Script started >> "%LOGFILE%"

:waitloop
if exist "REPLACE WITH SHARED FOLDER PATH" (
    echo [%date% %time%] Folder found, sharing... >> "%LOGFILE%"
    net share EPIC_PROJECT="REPLACE WITH SHARED FOLDER PATH" /grant:everyone,full >> "%LOGFILE%" 2>&1
    goto mapdrive
)
timeout /t 10
echo [%date% %time%] Waiting for folder... >> "%LOGFILE%"
goto waitloop

:mapdrive
echo [%date% %time%] Mapping drive... >> "%LOGFILE%"
net use X: \\USER\EPIC_PROJECT /persistent:yes
echo [%date% %time%] Drive mounted, script finalized >> "%LOGFILE%"