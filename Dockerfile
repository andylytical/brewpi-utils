FROM python:3

#ENV TZ=America/Chicago
#RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /src
COPY . /src
RUN pip install -r /src/requirements.txt

CMD ["bash"]
