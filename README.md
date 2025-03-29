## DB install Guide 

We are going to use PostgreSQL, so we need to create a Database first
To create the DB you have to download and install PostgreSQL

```
https://www.postgresql.org/download/
```
Then open bash and connect to the DB server:

```
psql -U your_username
```

Run the command to create a DB

```
CREATE DATABASE <DB_NAME>
```

Now go ahed and connect evrything together 



## Project Install guide

In bash terminal

```
git clone https://github.com/GoIT-Python-Web/Back-end-Python-Web-PhotoShare.git
cd Back-end-Python-Web-PhotoShare
poetry install
poetry shell
```


Then you have to create .env.development in src/conf/ 

```
cd src/conf/
touch .env.development
```

### **structure of .env.development**


```
ENV_APP=development
DB_URL=postgresql+asyncpg://<USERNAME>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME>

ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256
SECRET_KEY=your-super-secret

CLD_NAME=your-cloud-name
CLD_API_KEY=1234567890
CLD_API_SECRET=your-cloud-secret
```

Last stage is Make the first migration to create tables 

```
alembic upgrade head
```

