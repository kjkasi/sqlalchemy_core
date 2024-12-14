FROM python:3.10

WORKDIR /app
COPY ./requirements.txt /app/requirements.txt

RUN python -m pip install -r requirements.txt
RUN python -m pip install --disable-pip-version-check debugpy -t /tmp

RUN python -m pip install -r requirements.txt
RUN python -m pip install --disable-pip-version-check debugpy -t /tmp

# RUN curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg

#Download appropriate package for the OS version
#Choose only ONE of the following, corresponding to your OS version

#Debian 12
RUN curl https://packages.microsoft.com/config/debian/12/prod.list | tee /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update
RUN ACCEPT_EULA=Y apt-get install -y msodbcsql17
# optional: for bcp and sqlcmd
RUN ACCEPT_EULA=Y apt-get install -y mssql-tools
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
# RUN source ~/.bashrc
# optional: for unixODBC development headers
RUN  apt-get install -y unixodbc-dev
# optional: kerberos library for debian-slim distributions
RUN apt-get install -y libgssapi-krb5-2

ENTRYPOINT [ "python", "/tmp/debugpy", "--listen", "0.0.0.0:5678", "-m", "fastapi", "dev", "--host", "0.0.0.0", "--port", "8000", "main.py" ]
# ENTRYPOINT tail -F /dev/null