web: gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --host=0.0.0.0 --port=${PORT=-8000}