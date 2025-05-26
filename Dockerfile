FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y wget unzip libnss3 libgconf-2-4 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libgbm1 libgtk-3-0 libnspr4
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -x google-chrome-stable_current_amd64.deb /opt/chrome && \
    rm google-chrome-stable_current_amd64.deb
RUN wget https://chromedriver.storage.googleapis.com/126.0.6478.126/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm chromedriver_linux64.zip
ENV PATH="${PATH}:/opt/chrome/opt/google/chrome:/usr/local/bin"
RUN pip install -r requirements.txt
CMD ["python3", "scrapper.py"]
