# slimmed down image
FROM python:3.9-alpine

# ensuring there's no residue in case of failure
ENV PYTHONUNBUFFERED 1

RUN apk add --update --no-cache postgresql-client jpeg-dev
#temp postgres dependencies
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

RUN apk add libffi-dev


#app user variables
ARG user=app
ARG group=docker
ARG home=/home/$user
RUN addgroup -S $group && adduser -S $user -G $group

#create and copy over the code onto the container
RUN mkdir /sfs
COPY . /sfs/

# give user:group the permissions to the directory
RUN chown -R $user:$group /sfs/
RUN chmod -R 755 /sfs/

# Create local environment and use as variable
USER $user
ENV VIRTUAL_ENV=$home/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
# install requirements
RUN pip install -r /sfs/requirements.txt



# come back as root to clean up
USER root
# no need for temp dependencies anymore
RUN apk del .tmp-build-deps


# all future commands should run as the appuser user
USER $user
WORKDIR /sfs


