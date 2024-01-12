# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container to /app
WORKDIR /src

# Copy the current directory contents into the container at /app
COPY . /src

# Install any needed packages specified in requirements.txt
RUN pip install unstructured
RUN pip install -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run app.py when the container launches
CMD [ "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000" ]


