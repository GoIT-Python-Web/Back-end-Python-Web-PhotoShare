In bash terminal

1) git clone
2) cd <project_name>
3) poetry install
4) 

Then you should create .env.development in serc/conf/ 

structure of .env.development

ENV_APP=development
DB_URL=postgresql+asyncpg://<USERNAME>:<PASSWORD>@<HOST>:<PORT>/<DB_NAME>
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256
SECRET_KEY=your-super-secret

CLD_NAME=your-cloud-name
CLD_API_KEY=1234567890
CLD_API_SECRET=your-cloud-secret

5) alembic upgrade head



