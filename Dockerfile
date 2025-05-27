FROM docker.io/python:3.13.3
WORKDIR /src
COPY src /src
COPY requirements.txt /src
RUN python3 -m pip install -r requirements.txt
EXPOSE 5000
CMD ["python3","Simulation.py","-vf","-fp"]