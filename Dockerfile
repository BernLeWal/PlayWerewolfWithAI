FROM python:3.10-slim

RUN apt-get update 

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY agents /var/wairewolves/agents
COPY doc /var/wairewolves/doc
COPY logic /var/wairewolves/logic
COPY model /var/wairewolves/model
COPY util /var/wairewolves/util
COPY .env /var/wairewolves/
COPY *.py /var/wairewolves/
COPY *.md /var/wairewolves/

WORKDIR /var/wairewolves
CMD ["sh", "-c", "python ./moderator_bot.py"]
