FROM alpine:latest
WORKDIR /app
ARG DISCORD_TOKEN
ARG CHANNEL_ID
ARG GUILD_ID
# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN apk add --no-cache py3-pip
COPY requiremnts.txt requiremnts.txt
RUN apk add requiremnts.txt
COPY . .
RUN apk add -y ffmpeg
CMD [ "python3", "main.py" ]