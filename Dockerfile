# slimmed down image
FROM python:3.9-alpine

# ensuring there's no residue in case of failure
ENV PYTHONUNBUFFERED 1

# alpine patching
RUN apk add --update --no-cache postgresql-client jpeg-dev
#temp postgres dependencies
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

RUN apk add libffi-dev


#app user variables
ARG user=app
ARG group=docker
ARG home=/home/$user
ARG project=$home/sfs

RUN addgroup -S $group
RUN adduser --disabled-password \
    -g "" \
    -h $home \
    -G $group \
    $user

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
RUN apk del .tmp-build-deps

# & ensure user:group have the permissions to the directory
RUN chown -R $user:$group $project
RUN chmod -R 755 $project

# all future commands should run as the user
USER $user
WORKDIR $project


