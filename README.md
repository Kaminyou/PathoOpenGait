# PathoOpenGait

## Get started
1. Please modify `database/sql/create_user.sql` first to create accounts for default admin users.
2. Please create an `.env` file with the following format.
```env
JWT_SECRET_KEY=...
MYSQL_ROOT_PASSWORD=...
SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:<MYSQL_ROOT_PASSWORD>@db:3306/ndd
```
3. Execute
```
$ docker-compose up --build -d
```