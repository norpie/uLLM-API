FROM rocm/dev-ubuntu-24.04:6.2-complete

WORKDIR /app

COPY requirements-rocm.txt ./
COPY requirements.txt ./

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get -y install cmake git
RUN apt-get install -y python3.12 python3.12-dev

RUN python3.12 -m pip install --no-cache-dir -r "requirements-rocm.txt" --index-url "https://download.pytorch.org/whl/nightly/rocm6.2/" --break-system-packages
RUN python3.12 -m pip install --no-cache-dir -r "requirements.txt" --break-system-packages

EXPOSE 8080

COPY . .

CMD [ "python3.12", "./main.py", "--data-dir", "/data", "--http", "--host", "0.0.0.0" ]
