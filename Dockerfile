# Use official Python base image
FROM python:3.10-slim

# Set display environment variable for headless Chrome
ENV DISPLAY=:99

# Install system dependencies
# wget, gnupg, unzip, curl for general purposes
# xvfb for virtual display for headless Chrome
# fonts-liberation, libappindicator3-1, libatk-bridge2.0-0, libdrm2, libgtk-3-0, libnspr4, libnss3,
# libx11-xcb1, libxcomposite1, libxdamage1, libxrandr2, xdg-utils, libxss1, libxcb1, libgbm1,
# libu2f-udev, libvulkan1 are common dependencies for Chrome on Linux
# jq for parsing JSON to dynamically get ChromeDriver URL
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    xvfb \
    fonts-liberation \
    libappindicator3-1 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    libxss1 \
    libxcb1 \
    libgbm1 \
    libu2f-udev \
    libvulkan1 \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# Install ChromeDriver dynamically
# This script fetches the correct ChromeDriver version matching the installed Chrome browser.
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d'.' -f1-3) && \
    CHROMEDRIVER_URL=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json" | \
        jq -r --arg version "$CHROME_VERSION" '.versions[] | select(.version | startswith($version)) | .downloads.chromedriver[] | select(.platform=="linux64") | .url' | head -1) && \
    wget -O /tmp/chromedriver.zip "$CHROMEDRIVER_URL" && \
    unzip -o /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver.zip /tmp/chromedriver-linux64

# Set working directory inside the container
WORKDIR /app

# Copy your application code and test files into the container
# This assumes your Dockerfile is in the root of your project,
# and your test script (test_guestbook.py) and requirements.txt are also there.
COPY . .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Default command to run when the container starts
# xvfb-run -a: Runs a command in a new X server display. -a automatically picks a display number.
# python3 test_guestbook.py: Executes your Selenium test script.
# The APP_URL will be passed as a command-line argument when running from Jenkins.
CMD xvfb-run -a python3 test.py
