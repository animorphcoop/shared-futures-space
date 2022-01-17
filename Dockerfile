FROM python:3.9

# ensuring there's no residue in case of failure
ENV PYTHONUNBUFFERED 1

# alpine patching - postgres dependencies and bridging
#RUN apk add --update --no-cache postgresql-client jpeg-dev
#RUN apk add --update --no-cache --virtual .tmp-build-deps \
#    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
#RUN apk add libffi-dev

# alpine NPM
#RUN apk add --update --no-cache npm

# app user variables
ARG user=app
ARG group=docker
ARG home=/home/$user
ARG project=$home/sfs

# import from docker-compose - receive the current host user and their main group IDs
ARG USERID
ARG GROUPID

# create group and user with home directory
# alpine version: RUN addgroup -g $GROUPID $group && adduser -u $USERID -G $group -h $home -D $user
RUN addgroup --gid $GROUPID $group
RUN adduser -u $USERID --ingroup $group --home $home --disabled-password $user

# switch to new user
USER $user

#create directory and copy over the code onto the container
RUN mkdir $project
COPY . $project/

# Create local environment and use as variable
ENV VIRTUAL_ENV=$home/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# install requirements
RUN pip install -r $project/requirements.txt

# come back as root to clean up
USER root

# no need for temp dependencies anymore
# RUN apk del .tmp-build-deps

# all future commands should run as the user in project directory
USER $user
WORKDIR $project
