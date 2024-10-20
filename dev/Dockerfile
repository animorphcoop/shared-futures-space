# Dockerfile development
FROM python:3.10
ENV PYTHONUNBUFFERED 1

# install node
RUN apt-get update \
    && apt-get install -y ca-certificates curl gnupg binutils libproj-dev gdal-bin geos-bin \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg

# app user variables
ARG user=app
ARG group=docker
ARG home=/home/$user
ARG project=$home/sfs

# import from docker-compose - receive the current host user and their main group IDs
ARG USERID
ARG GROUPID

# create group and user with home directory
RUN addgroup --gid $GROUPID $group
RUN adduser -u $USERID --ingroup $group --home $home --disabled-password $user

# switch to new user
USER $user

# create directory
RUN mkdir $project

# install requirements in venv
COPY ../prod/requirements.txt $project/
ENV VIRTUAL_ENV=$home/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# install requirements
RUN pip install -r $project/requirements.txt

# install dev requirements
COPY dev/requirements_dev.txt $project/
RUN pip install -r $project/requirements_dev.txt

# copy over the code onto the container
COPY .. $project/

WORKDIR $project
