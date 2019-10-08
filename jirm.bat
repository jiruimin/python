ls_date=`date +%Y%m%d`
git-pull() {
    echo git fetch --all && git reset --hard origin/master && git pull ...
    git fetch --all && git reset --hard origin/master && git pull
    echo  The pull end!
}
git-push() {
    echo git add . && git commit -m $ls_date && git push origin master ...
    git add . && git commit -m $ls_date && git push origin master
    echo  The push end!
}
case "$1" in
        git-pull)
          git-pull
           ;;

        git-push)
          git-push
           ;;

           *)
          echo "usage git-pull|git-push"
           ;;

esac

