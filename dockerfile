FROM python:3.13-slim-bookworm
WORKDIR /app
ARG DISCORD_TOKEN
ARG CHANNEL_ID
ARG GUILD_ID
COPY requiremnts.txt requiremnts.txt
RUN pip3 install -r requiremnts.txt
COPY . .
RUN apt-get update && apt-get install -y ffmpeg
RUN touch config/db/Exorcists.db
CMD [ "python3", "main.py" ]