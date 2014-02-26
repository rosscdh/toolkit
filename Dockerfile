FROM orchardup/python:2.7

RUN apt-get update -qq && apt-get install -y build-essential libxml2-dev libxslt1-dev python-setuptools python-dev apache2-utils uwsgi-plugin-python libjpeg8 libjpeg62-dev libfreetype6 libfreetype6-dev nmap htop vim unzip git-core mercurial subversion libtidy-dev postgresql-client libpq-dev python-psycopg2

RUN mkdir /toolkit
WORKDIR /toolkit
ADD requirements.txt /toolkit/
ADD . /toolkit/
RUN pip install -r /toolkit/requirements/dev.txt --use-mirrors

RUN mkdir /stamp
WORKDIR /stamp
ADD ../Stamp/* /stamp/
