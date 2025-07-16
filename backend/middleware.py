import psycopg
from decouple import config
from django.utils.deprecation import MiddlewareMixin

class EnsureDatabaseExistsMiddleware(MiddlewareMixin):
    checked = False

    def process_request(self, request):
        if EnsureDatabaseExistsMiddleware.checked:
            return
        db_host = config('DB_HOST', default='localhost')
        db_port = config('DB_PORT', default='5432')
        db_user = config('DB_USER', default='postgres')
        db_password = config('DB_PASSWORD', default='')
        db_name = config('TARGET_DB_NAME', default='team_management')
        try:
            # Try connecting to the target DB
            psycopg.connect(
                dbname=db_name, user=db_user, password=db_password,
                host=db_host, port=db_port
            ).close()
        except psycopg.OperationalError:
            # If it fails, connect to 'postgres' and create the DB
            con = psycopg.connect(
                dbname='postgres', user=db_user, password=db_password,
                host=db_host, port=db_port,
                autocommit=True
            )
            cur = con.cursor()
            cur.execute(f'CREATE DATABASE "{db_name}"')
            cur.close()
            con.close()
        EnsureDatabaseExistsMiddleware.checked = True 