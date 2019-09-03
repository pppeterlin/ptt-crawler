# User an official Python runtime as a parent image
FROM python:3.6-slim

# Set the working directory to  /.py
WORKDIR /Users/peterlin/Documents/Python/ptt-crawler/

# Copy the current directory contents into the container at /.py
COPY . /Users/peterlin/Documents/Python/ptt-crawler/

# Install needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Define environment variable
ENV NAME googleAPI

# Run macshop.py when the contain launches
CMD ["python3", "macshop.py"]