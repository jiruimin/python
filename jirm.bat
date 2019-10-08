REM @echo off
set var1=%date%
set op=%1
if "%op%"=="git-pull" ( 
  git fetch --all && git reset --hard origin/master && git pull 
  echo  The pull end!
) else if "%op%"=="git-push" (
  git add . && git commit -m $var1 && git push origin master
  echo  The push end!
) else (
  echo "usage git-pull|git-push"
)

