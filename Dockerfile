FROM mcr.microsoft.com/playwright/python:v1.41.0-jammy

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY facebook_group_scraper.py .

# Create output directory
RUN mkdir -p output

# Run the application
CMD ["python", "facebook_group_scraper.py"]
