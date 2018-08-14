FROM python:3

#ENV TZ=America/Chicago
#RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /src
COPY brewpi-backup/requirements.txt /src/
COPY brewpi-backup/*.py /src/
COPY submodules/*/*.py /src/
RUN pip install -r /src/requirements.txt

CMD ["python", "brewpi_backup.py"]
