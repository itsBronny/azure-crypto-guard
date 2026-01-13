# 1. Base Image: Start with a lightweight version of Python 3.9
# logic: "slim" means it has the bare minimum tools to run Python.
FROM python:3.9-slim

# 2. Work Directory: Create a folder inside the container named /code
# logic: This is like doing 'mkdir /code' and 'cd /code'.
WORKDIR /code

# 3. Copy Requirements: Move our text file from your computer into the container
# logic: We copy this FIRST to take advantage of Docker "caching".
COPY ./app/requirements.txt /code/requirements.txt

# 4. Install Dependencies: specific command to install libraries
# logic: --no-cache-dir keeps the image small. -r reads from the file.
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 5. Copy Code: Move your entire 'app' folder into the container
# logic: Now that libraries are installed, we bring in our actual logic.
COPY ./app /code/app

# 6. Command: The instruction to run when the container starts
# logic: 'uvicorn' starts the server. 'app.main:app' tells it where to look.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]