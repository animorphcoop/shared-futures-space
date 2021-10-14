# slimmed down image
FROM python:3.9-alpine

# ensuring there's no residue in case of failure
ENV PYTHONUNBUFFERED 1

RUN mkdir /sfs
COPY requirements.txt /sfs/

RUN apk add --update --no-cache postgresql-client jpeg-dev
#temp postgres dependencies
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

# install dependencies
# TODO: causes warning - "Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager"
RUN pip install -r /sfs/requirements.txt

# Solves the Warning on global/root pip but causes "Cannot start service celery: failed to create shim: OCI runtime create failed: container_linux.go:380: starting container process caused: exec: "celery": executable file not found in $PATH: unknown"
#RUN python -m venv venv && source venv/bin/activate && pip install -r /sfs/requirements.txt


# no need for temp dependencies anymore
RUN apk del .tmp-build-deps

#create and copy over the code onto the container

COPY . /sfs/

# create a group, user and add user to the group
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
# give user:group the permissions to the directory
RUN chown -R appuser:appgroup /sfs
# all future commands should run as the appuser user
USER appuser

WORKDIR /sfs

