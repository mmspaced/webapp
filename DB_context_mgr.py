import psycopg2

class DBConnectionError(Exception):
    pass

class SQLError(Exception):
    pass

class UseDatabase:

    def __init__(self, config:dict) -> None:
        self.configuration = config

    def __enter__(self) -> 'cursor':
        try:
            self.conn = psycopg2.connect(**self.configuration)
            self.cursor = self.conn.cursor()
            return self.cursor

        # When an exception is raised within the with suite and not caught,
        # the context manager terminates the with suite's code and jumps to
        # the __exit__ method and passes in the exception's type, value,
        # and traceback information

        except psycopg2.OperationalError as err:
            raise DBConnectionError(err)

        except psycopg2.ProgrammingError as err:
            raise SQLError(err)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

        # Adding exception processing logic here ensures that the __exit__
        # method does its clean up before any passed in exceptions are
        # dealt with.

        if exc_type is psycopg2.ProgrammingError:
            raise SQLError(exc_val)
        elif exc_type:
            raise exc_type(exc_val)
