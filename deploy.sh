#!/bin/bash

# current issue: collectstatic /home/app/sfs/static vs /home/app/sfs/sfs/static

echo "# ensuring tests are passing"
test_result=$(python <<'ENDPY'
import requests
session = requests.Session()
session.headers.update({'PRIVATE-TOKEN': '8N919pt1XMHwFq8MA2Ev'})
last_commit = session.get('https://git.coop/api/v4/projects/1108/repository/branches/staging').json()['commit']['id']
last_commit_tests = session.get('https://git.coop/api/v4/projects/1108/repository/commits/'+str(last_commit)).json()['last_pipeline']['id']
tests_status = session.get('https://git.coop/api/v4/projects/1108/pipelines/'+str(last_commit_tests)).json()['status']
print(tests_status)
ENDPY
)
echo "# test result: $test_result"
if [[ "$test_result" != "success" ]];
then
  echo "# TESTS ARE NOT PASSING FOR LATEST COMMIT ON STAGING, WILL NOT DEPLOY"
  exit
else
  echo "# tests pass, deploying"
fi

echo "# DEPLOY TO PRODUCTION (REALLY REAL WORLD FOR REAL)?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) break;;
        No ) echo "# CANCELLED"; exit;;
    esac
done

echo "# DEPLOYING TO PRODUCTION"

ssh $(whoami)@sharedfutures.webarch.net 'bash -s' <<'ENDSSH'
  # The following commands run on the remote host
  sudo su - dev
  cd sites/dev
  echo "# stopping docker-compose"
  docker-compose stop > /dev/null
  if [[ "$(git rev-parse --abbrev-ref HEAD)" != "staging" ]];
  then
    echo "# checking out staging"
    git checkout staging > /dev/null
  fi
  echo "# pulling from staging"
  git pull --no-rebase https://asa:ukFKuw9kCLc5Y2z9dPvy@git.coop/animorph-coop/shared-futures-space.git staging > /dev/null
  if [[ $? -ne 0 ]];
  then
    echo "# FAILED TO PULL FROM STAGING"
    echo "# RESTARTING DOCKER-COMPOSE WITHOUT DEPLOYING"
  else
    echo "# restarting docker-compose"
  fi
  docker-compose start > /dev/null
  echo "# collecting static files"
  exit
  docker-compose exec -u root app chown app:docker -R /home/app/sfs/static
  docker-compose exec app python3 manage.py collectstatic > /dev/null
  echo "# running tests locally"
  docker-compose exec app python3 pytest tests
  if [[ $? -ne 0 ]];
  then
    echo "##########################"
    echo "#   TESTS FAIL LOCALLY!"
    echo "##########################"
    echo "# this requires attention!"
  else
    echo "# TESTS SUCCEED, DEPLOYED SUCCESSFULLY"
  fi
ENDSSH
