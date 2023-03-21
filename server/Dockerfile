FROM python:3.6
MAINTAINER Mathias Schmoigl <mathias.schmoigl-tonis@salzburgresearch.at>
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 8083
ENTRYPOINT ["python"]
CMD ["app.py"]
