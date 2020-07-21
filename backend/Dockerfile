FROM python:3.8-slim-buster AS dependencies

COPY requirements.txt  ./

RUN pip install -U pip wheel                        \
  && apt-get update                                 \
  && apt-get install -y                             \
        git                                         \
        --no-install-recommends                     \
  && apt-get clean                                  \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*  \
  && pip install --upgrade -r requirements.txt

FROM dependencies AS dev

WORKDIR /usr/backend

COPY requirements.test.txt  ./

RUN pip install -r requirements.test.txt            \
  && apt-get update                                 \
  && apt-get install -y                             \
        make                                        \
        --no-install-recommends                     \
  && apt-get clean                                  \
  && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY . .

RUN pip install . \
  &&  python setup.py sdist bdist_wheel


ENTRYPOINT [ "make" ]

FROM dependencies

WORKDIR /usr/backend

COPY --from=dev /usr/backend/dist/*.whl /usr/backend/
RUN pip install `ls *.whl`

CMD ["gunicorn_anyblok_uvicorn", "--anyblok-configfile", "/etc/app.cfg", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "60"]
