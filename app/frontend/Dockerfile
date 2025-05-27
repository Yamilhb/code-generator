FROM python:3.12-slim

WORKDIR /app

# Copia solo los archivos necesarios para el frontend
COPY streamlit_app.py .  
COPY requirements.txt .

# Instala solo lo necesario
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--reload"]
