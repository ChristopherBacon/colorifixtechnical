# Base image
FROM python:3.11.4-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy the application code to the container
COPY . .

# Expose the port that the FASTAPI application will run on
EXPOSE 8000


# Set environment variables for Neo4j connection
ENV NEO4J_URI "bolt://localhost:7687"
ENV NEO4J_USER "neo4j"
ENV NEO4J_PASSWORD "password"

# Start the FASTAPI application
CMD ["uvicorn", "colorifix_technical:app", "--host", "0.0.0.0", "--port", "8000"]