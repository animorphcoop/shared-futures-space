#!/bin/bash

# current issue: collectstatic /home/app/sfs/static vs /home/app/sfs/sfs/static

echo "# ensuring tests are passing"
test_result=$(python <<'ENDPY'
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

echo "# security check to prevent public credentials being used"
check_result=$(python <<'ENDPY'
import requests
session = requests.Session()
session.headers.update({'PRIVATE-TOKEN': 'ameaqjp9RMWxVtnnzTaD'})
app_env = session.get('https://git.coop/api/v4/projects/1108/repository/files/app_variables.env?ref=staging')
db_env = session.get('https://git.coop/api/v4/projects/1108/repository/files/db_pg_variables.env?ref=staging')
local = session.get('https://git.coop/api/v4/projects/1108/repository/files/sfs%2Fsettings%2Flocal.py?ref=staging')
ci = session.get('https://git.coop/api/v4/projects/1108/repository/files/.gitlab-ci.yml?ref=staging')
print([f.json()['file_path'] for f in [app_env, db_env, local, ci] if (f.status_code == 200)])
ENDPY
)
if [[ "$check_result" != "[]" ]];
then
  echo "# STAGING BRANCH CONTAINS DEFAULT CREDENTIAL FILES:"
  echo "# $check_result"
  echo "# WILL NOT DEPLOY"
  exit
else
  echo "# security check passed"
fi

echo "# DEPLOY TO PRODUCTION (REALLY REAL WORLD FOR REAL)?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) break;;
        No ) echo "  # CANCELLED"; exit;;
    esac
done
echo "# REQUIRES REBUILD OF CONTAINERS?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) echo "# WILL REBUILD CONTAINERS"; rebuild_required=1; break;;
        No ) echo "# WILL NOT REBUILD CONTAINERS"; rebuild_required=0; break;;
    esac
done

echo "# DEPLOYING TO PRODUCTION"

ssh $(whoami)@sharedfutures.webarch.net 'bash -s' <<ENDSSH
  # The following commands run on the remote host
  sudo su - dev
  cd sites/dev
  echo "# stopping docker-compose"
  USER_ID=\$(id -u) GROUP_ID=\$(id -g) docker-compose stop > /dev/null
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
      if [[ \$exit_code -ne 0 ]];
      then
        echo "##########################"
        echo "#   TESTS FAIL LOCALLY!"
        echo "##########################"
        echo "# this requires attention!"
        echo "# test are: docker-compose exec app pytest tests"
      else
        echo "# TESTS SUCCEED, DEPLOYED SUCCESSFULLY"
      fi' | USER_ID=\$(id -u) GROUP_ID=\$(id -g) docker-compose exec -T app sh
  fi
ENDSSH
