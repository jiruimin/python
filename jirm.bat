@echo off
set date=%date%
set op=%1
if "%op%"=="git-pull" ( 
  echo ---------"git fetch --all && git reset --hard origin/master && git pull origin master"...
  git fetch --all && git reset --hard origin/master && git pull origin master
  echo  The pull end!
) else if "%op%"=="git-push" (
  echo ---------"git add . && git commit -m "%date%" && git push origin master"...
  git add . && git commit -m "%date%" && git push origin master
  echo  The push end!
) else (
  echo "usage git-pull|git-push"
)

