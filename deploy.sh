#!/bin/bash

# gitlab settings
GITLAB_PROJECT_URL='https://git.coop/api/v4/projects/1108'
GITLAB_TOKEN='ameaqjp9RMWxVtnnzTaD'

# deploy settings
TARGET_SERVER='sharedfutures.webarch.net'
REBUILD_REQUIRED=0
TARGET_DIR=''
TARGET_DATA_DIR=''

# figure out remote user (defaults to current user on local)
REMOTE_USER=$(whoami)
if [ -n "$1" ];
then
  REMOTE_USER=$1
fi

# check_tests makes a gitlab request and verifies that CI has passed
# successfully on the latest commit of the staging branch
check_tests() {
  echo "# ensuring tests are passing on gitlab"
  response=$(curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "$GITLAB_PROJECT_URL/repository/branches/staging")
  last_commit=$(echo "$response" | jq -r '.commit.id')

  if [ "$last_commit" == "null" ]; then
    echo "GITLAB API FAILURE, IS THE TOKEN STILL VALID?"
    exit
  fi

  response=$(curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "$GITLAB_PROJECT_URL/repository/commits/$last_commit")
  last_commit_tests=$(echo "$response" | jq -r '.last_pipeline.id')

  if [ "$last_commit_tests" == "null" ]; then
    echo "GITLAB API FAILURE, UNABLE TO GET LAST PIPELINE ID"
    exit
  fi

  response=$(curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "$GITLAB_PROJECT_URL/pipelines/$last_commit_tests")
  tests_status=$(echo "$response" | jq -r '.status')

  echo "# test result: $tests_status"
  if [ "$tests_status" != "success" ]; then
    echo "# TESTS ARE NOT PASSING FOR LATEST COMMIT ON STAGING, WILL NOT DEPLOY"
    exit
  else
    echo "# tests pass"
  fi
}

# input_dev_prod asks the user to choose whether to deploy on
# dev.sharedfutures.space or sharedfutures.space
input_dev_prod() {
  echo "# DEPLOY TO DEVELOPMENT/PRODUCTION (REALLY REAL WORLD FOR REAL)?"
  select opt in "Development" "Production" "Cancel"; do
      case $opt in
          Development ) target_user="dev"; TARGET_DIR="/home/dev/sites/dev"; TARGET_DATA_DIR="/home/dev/sites/dev_data"; break;;
          Production ) target_user="prod"; TARGET_DIR="/home/prod/sites/prod"; TARGET_DATA_DIR="/home/prod/sites/prod_data"; break;;
          Cancel ) echo "# CANCELLED"; exit;;
      esac
  done
}

# input_rebuilt asks the user whether to also rebuild docker containers when deploying
input_rebuilt() {
  echo "# REQUIRES REBUILD OF CONTAINERS? (THIS WOULD ERASE THE DATABASE)"
  select yn in "Yes" "No"; do
      case $yn in
          Yes ) echo "# WILL REBUILD CONTAINERS"; REBUILD_REQUIRED=1; break;;
          No ) echo "# WILL NOT REBUILD CONTAINERS"; REBUILD_REQUIRED=0; break;;
      esac
  done
}

# check_files ensures that essential for deployment files exist on remote dev/prod server
check_files() {
  ssh $REMOTE_USER@$TARGET_SERVER 'bash -s' <<ENDSSH
    # The following commands run on the remote host
    if sudo -u $target_user test ! -f $TARGET_DATA_DIR/variables.env || sudo -u $target_user test ! -f $TARGET_DATA_DIR/secrets.py || sudo -u $target_user test ! -f $TARGET_DATA_DIR/settings.py || sudo -u $target_user test ! -f $TARGET_DATA_DIR/docker-compose.override.yaml;
    then
      echo "# COULD NOT FIND ALL REQUIRED LOCAL SETTINGS FILES"
      echo "# wanted $TARGET_DATA_DIR/variables.env, secrets.py, settings.py and docker-compose.override.yaml"
      echo "# WILL NOT DEPLOY WITHOUT LOCAL SETTINGS BECAUSE DEFAULTS INCLUDE CREDENTIALS"
      exit
    else
      echo "# FOUND ALL REQUIRED LOCAL SETTINGS FILES"
    fi
ENDSSH
}

# restart_docker pulls latest git changes and restarts docker containers on remote dev/prod server
restart_docker() {
  ssh $REMOTE_USER@$TARGET_SERVER 'bash -s' <<ENDSSH
    sudo su - $target_user
    cd $TARGET_DIR
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
      echo "# installing local settings files from $TARGET_DATA_DIR"
      cp $TARGET_DATA_DIR/variables.env $TARGET_DIR
      cp $TARGET_DATA_DIR/secrets.py $TARGET_DIR/sfs/settings/
      cp $TARGET_DATA_DIR/settings.py $TARGET_DIR/sfs/settings/
      cp $TARGET_DATA_DIR/docker-compose.override.yaml $TARGET_DIR
      if [[ $REBUILD_REQUIRED -eq 1 ]];
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
}

echo "# DEPLOY SCRIPT II"
check_tests
input_dev_prod
input_rebuilt
echo "# DEPLOYING TO PRODUCTION OR DEVELOPMENT"
check_files
restart_docker
