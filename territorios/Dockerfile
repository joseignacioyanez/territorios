FROM python:3.10.1-alpine3.15

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV GOOGLE_MAPS_API_KEY = "AIzaSyD4HT3e9VI8MessL8ZorAcKgoA8YYGyhoU"
ENV TELEGRAM_BOT_TOKEN = "5937302183:AAHxqvoy9UjAIVIMlDUp6J7ny6y3D8X9brw"
ENV TELEGRAM_ADMIN_CHAT_ID = "334575560"

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app

# Install any dependencies specified in requirements.txt
RUN pip install -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Run the Django development server
CMD ["python", "territorios/manage.py", "runserver", "0.0.0.0:8000"]