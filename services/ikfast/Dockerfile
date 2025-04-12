FROM hamzamerzic/openrave-py3

RUN pip install --break-system-packages fastapi uvicorn python-multipart

COPY app.py /app/app.py
WORKDIR /app

EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
