FROM python:3.13-slim-bookworm
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
RUN apt-get update && apt-get install -y ffmpeg sqlite3 fontconfig fonts-liberation && rm -rf /var/lib/a
RUN mkdir -p /app/config/db /app/config/images
COPY config/images/IDCard.png /app/config/images/IDCard.png
COPY config/images/ID2.png /app/config/images/ID2.png
RUN ls -la /app/config/images/ || echo "Files not found in /app/config/images/"
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
