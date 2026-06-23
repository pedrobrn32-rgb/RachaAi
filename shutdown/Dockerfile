FROM python:3.11-slim

WORKDIR /app

# Copy the requirements file from the build context root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files from the build context root into the container
COPY . .

ENV PORT=8081

CMD ["python", "main.py"]