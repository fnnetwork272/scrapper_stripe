FROM python:3.10-slim

WORKDIR /app
COPY . .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    libnss3 \
    libgconf-2-4 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -x google-chrome-stable_current_amd64.deb /opt/chrome && \
    chmod +x /opt/chrome/opt/google/chrome/google-chrome && \
    rm google-chrome-stable_current_amd64.deb

# Set PATH for Chrome
ENV PATH="${PATH}:/opt/chrome/opt/google/chrome"

# Install ChromeDriver
RUN CHROMEDRIVER_VERSION="127.0.6533.119" && \
    echo "Installing ChromeDriver version: ${CHROMEDRIVER_VERSION}" && \
    wget -q https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm chromedriver_linux64.zip

# Verify installations
RUN google-chrome --version || echo "Chrome version check failed" && \
    chromedriver --version || echo "ChromeDriver version check failed"

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the application
CMD ["python", "scrapper.py"]
