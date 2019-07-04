FROM registry.access.redhat.com/ubi8/python-36
ENV PYTHONUBUFFERED 1
WORKDIR /opt/app-root/src
COPY requirements.txt /opt/app-root/src
RUN pip install -r requirements.txt
COPY . /opt/app-root/src
