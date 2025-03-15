# Use official Python image
FROM python:3.12

# Set working directory inside the container
WORKDIR /app

# Copy the dependency file and install required packages
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application
COPY . .

# Expose port 8000 for Django
EXPOSE 8000

# Run migrations and start the Django server
CMD ["sh", "-c", "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
