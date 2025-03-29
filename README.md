In bash terminal

1) git clone https://github.com/GoIT-Python-Web/Back-end-Python-Web-PhotoShare.git
2) cd Back-end-Python-Web-PhotoShare
3) poetry install
4) poetry shell


5) you have to create .env.development in serc/conf/ 
6) alembic upgrade head

structure of .env.development


```env
ENV_APP=development
DB_URL=postgresql+asyncpg://<USERNAME>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME>

ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256
SECRET_KEY=your-super-secret

CLD_NAME=your-cloud-name
CLD_API_KEY=1234567890
CLD_API_SECRET=your-cloud-secret



