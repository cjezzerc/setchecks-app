FROM python:3

RUN mkdir /app_home
WORKDIR /app_home
COPY . . 

RUN pip install -r requirements.txt
# try this to prevent this https://stackoverflow.com/questions/77222538/need-to-downgrade-to-werkzeug-2-3-7-from-werkzeug-3-0-0-to-avoid-werkzeug-http
RUN pip uninstall -y werkzeug
RUN pip install werkzeug==2.3.7 

RUN ["apt-get", "update"]
RUN ["apt-get", "install", "-y", "vim"]

EXPOSE 5000

CMD cd /app_home; python run_app.py
