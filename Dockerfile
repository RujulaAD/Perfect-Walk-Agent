# 1. Use a lightweight Python server
FROM python:3.11-slim

# 2. Set the working directory inside the server
WORKDIR /app

# 3. Copy manifest and install the libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy all python scripts into the server
COPY . .

# 5. Tell the server what port to use for the internet
EXPOSE 8080

# 6. The command to launch the app
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]