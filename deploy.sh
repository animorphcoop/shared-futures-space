#!/bin/bash

target_server="sharedfutures.webarch.net"
target_user="dev"
target_dir="/home/dev/sites/dev"
target_data_dir="/home/dev/sites/dev_data"
if [ -z "$1" ];
then
  remote_user=$(whoami)
else
  remote_user=$1
fi

echo "# DEPLOY SCRIPT II"

echo "# ensuring tests are passing"
test_result=$(python3 <<'ENDPY'
import requests
session = requests.Session()
session.headers.update({'PRIVATE-TOKEN': 'ameaqjp9RMWxVtnnzTaD'})
try:
  last_commit = session.get('https://git.coop/api/v4/projects/1108/repository/branches/staging').json()['commit']['id']
  last_commit_tests = session.get('https://git.coop/api/v4/projects/1108/repository/commits/'+str(last_commit)).json()['last_pipeline']['id']
  tests_status = session.get('https://git.coop/api/v4/projects/1108/pipelines/'+str(last_commit_tests)).json()['status']
  print(tests_status)
except Exception as e:
  print('GITLAB API FAILURE, IS THE TOKEN STILL VALID?')
ENDPY
)
echo "# test result: $test_result"
if [[ "$test_result" != "success" ]];
then
  echo "# TESTS ARE NOT PASSING FOR LATEST COMMIT ON STAGING, WILL NOT DEPLOY"
  exit
else
  echo "# tests pass"
fi

echo "# DEPLOY TO PRODUCTION (REALLY REAL WORLD FOR REAL)?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) break;;
        No ) echo "  # CANCELLED"; exit;;
    esac
done
echo "# REQUIRES REBUILD OF CONTAINERS? (THIS WOULD ERASE THE DATABASE)"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) echo "# WILL REBUILD CONTAINERS"; rebuild_required=1; break;;
        No ) echo "# WILL NOT REBUILD CONTAINERS"; rebuild_required=0; break;;
    esac
done

echo "# DEPLOYING TO PRODUCTION"

ssh $remote_user@$target_server 'bash -s' <<ENDSSH
  # The following commands run on the remote host
  if sudo -u $target_user test ! -f $target_data_dir/variables.env || sudo -u $target_user test ! -f $target_data_dir/local.py || sudo -u $target_user test ! -f $target_data_dir/settings.py;
  then
    echo "# COULD NOT FIND ALL REQUIRED LOCAL SETTINGS FILES"
    echo "# wanted $target_data_dir/variables.env, local.py and settings.py"
    echo "# WILL NOT DEPLOY WITHOUT LOCAL SETTINGS BECAUSE DEFAULTS INCLUDE CREDENTIALS"
    exit
  fi
  sudo su - $target_user
  cd $target_dir
  echo "# stopping docker-compose"
  USER_ID=\$(id -u) GROUP_ID=\$(id -g) docker-compose stop > /dev/null
  echo "# stashing so git won't complain"
  git stash > /dev/null
  if [[ "\$(git rev-parse --abbrev-ref HEAD)" != "staging" ]];
  then
    echo "# checking out staging"
    git checkout staging > /dev/null
  fi
  echo "# pulling from staging"
  git pull --no-rebase git@git.coop:animorph-coop/shared-futures-space.git
  if [[ \$? -ne 0 ]];
  then
    echo "# FAILED TO PULL FROM STAGING (IS THE SSH KEY .ssh/id_rsa.pub STILL ALLOWED BY AN ACCOUNT WITH ACCESS TO THE REPOSITORY?)"
    echo "# RESTARTING DOCKER-COMPOSE WITHOUT DEPLOYING"
    USER_ID=\$(id -u) GROUP_ID=\$(id -g) docker-compose start > /dev/null
    pull_failed=1
  else
    pull_failed=0
  fi
  if [[ \$pull_failed -eq 1 ]];
  then
    echo "# COULD NOT PULL FROM STAGING"
    echo "# DEPLOYMENT FAILED"
  else
    echo "# installing local settings files from /home/dev/sites/dev_data/"
    cp $target_data_dir/variables.env $target_dir
    cp $target_data_dir/local.py $target_dir/sfs/settings/
    cp $target_data_dir/settings.py $target_dir/sfs/settings/
    if [[ $rebuild_required -eq 1 ]];
    then
      echo "# REBUILDING CONTAINERS (THIS MAY TAKE SOME TIME)"
      USER_ID=\$(id -u) GROUP_ID=\$(id -g) docker-compose build > /dev/null
    else
      echo "# NOT REBUILDING CONTAINERS"
    fi
    echo "# restarting docker-compose"
    USER_ID=\$(id -u) GROUP_ID=\$(id -g) docker-compose start > /dev/null
    echo "# collecting static files"
    # extremely ugly solution to docker-compose's weird interactions with heredocs and ssh
    echo '
      python3 manage.py collectstatic --noinput > /dev/null
      echo "# running tests locally (may take a minute)"
      echo
      exit_code=0
      pytest tests > /dev/null || exit_code=\$?
      exit \$exit_code' | USER_ID=\$(id -u) GROUP_ID=\$(id -g) docker-compose exec -T app sh
    if [[ \$? -ne 0 ]];
    then
      echo "##########################"
      echo "#   TESTS FAIL LOCALLY!"
      echo "##########################"
      echo "# this requires attention!"
      echo "# test are: docker-compose exec app pytest tests"
    else
      echo "# TESTS SUCCEED, DEPLOYED SUCCESSFULLY"
    fi
  fi
ENDSSH
