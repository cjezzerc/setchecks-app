FROM python:3

RUN mkdir /app_home

WORKDIR /app_home

COPY VSMT_UPROT_APP .

#deal with rogue Windows line endings causing env to pick up wrong argument
RUN tr -d '\r' <run_app.py >clean_run_app.py 
RUN chmod +x clean_run_app.py

RUN pip install -r requirements.txt

EXPOSE 5000

CMD cd /app_home; ./clean_run_app.py
