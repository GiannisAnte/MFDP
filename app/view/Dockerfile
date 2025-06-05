FROM python:3.11-slim

WORKDIR /view

COPY requirements.txt /view/

RUN pip install --upgrade pip && pip install -r /view/requirements.txt

COPY . .

CMD ["streamlit", "run", "Home.py", "--server.port=8501", "--server.headless=true"]
