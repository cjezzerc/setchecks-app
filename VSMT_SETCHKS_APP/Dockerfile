FROM python:3

RUN mkdir /app_home

WORKDIR /app_home

# ????? next bitdepends if sharing code still with VSMT_UPROT_APP
COPY . . 

#deal with rogue Windows line endings causing env to pick up wrong argument
WORKDIR /app_home/VSMT_SETCHKS_APP
RUN tr -d '\r' <run_app.py >clean_run_app.py 
RUN chmod +x clean_run_app.py

RUN pip install -r requirements.txt

EXPOSE 5001

CMD cd /app_home/VSMT_SETCHKS_APP; ./clean_run_app.py
