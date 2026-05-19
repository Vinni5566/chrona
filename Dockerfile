FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Set Python path so the module is recognized
ENV PYTHONPATH=/app/src

# Create a generic mount point for scanning external repositories
VOLUME ["/workspace"]

# Run the CLI by default
ENTRYPOINT ["python", "-m", "chrona.cli.commands"]
CMD ["--help"]
