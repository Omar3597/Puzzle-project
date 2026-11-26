# Small image: slim Python + only the system package tkinter needs
FROM python:3.12-slim

# python3-tk is not needed (the official image has tkinter), but Tk needs these X11 libraries
RUN apt-get update \
    && apt-get install -y --no-install-recommends libtk8.6 libx11-6 libxft2 libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install only the required libraries (no cache = smaller image)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY puzzle.py algorithms.py app.py test_puzzle.py ./

CMD ["python", "app.py"]
