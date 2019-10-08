set var1=%date%;
if "%1"=="git-pull" (echo git fetch --all && git reset --hard origin/master && git pull ... 
  git fetch --all && git reset --hard origin/master && git pull 
  echo  The pull end!) else if "%1"=="git-push" ( echo git add . && git commit -m $ls_date && git push origin master ...
  git add . && git commit -m $ls_date && git push origin master
  echo  The push end!) else ( echo "usage git-pull|git-push" )

