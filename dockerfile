FROM python:3.14-slim

# The commands essentially run here
WORKDIR /usr/src/app 

# current directory with regards to working directory
# we separately copy requirements.txt because if there are changes
# in requirements it downloads it but if we do it later it will run 
# pip intsall on every single change making it not optimal
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# copy from current directory to current dockerfile WorkDirectory
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

