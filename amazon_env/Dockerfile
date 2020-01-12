FROM amazonlinux:2.0.20191217.0

RUN yum update -y \
    && yum install python3 zip -y

COPY entrypoint.sh /usr/local/bin/
WORKDIR /var/task

ENTRYPOINT [ "entrypoint.sh" ]
