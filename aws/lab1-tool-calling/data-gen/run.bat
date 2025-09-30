@echo off
setlocal

docker run ^
       --rm ^
       --env-file free-trial-license-docker.env ^
       --net=host ^
       -v %cd%/root.json:/home/root.json ^
       -v %cd%/generators:/home/generators ^
       -v %cd%/connections:/home/connections ^
       shadowtraffic/shadowtraffic:1.1.9 ^
       --config /home/root.json

if %ERRORLEVEL% neq 0 (
    echo Command failed with error code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo Command completed successfully