from django.db import connection


class SQLUtils:

    def reset_sql_sequence(self, model):

        sentence = """\
            SELECT
                setval(pg_get_serial_sequence('"{0}"','id'),
                coalesce(max("id"), 1), max("id") IS NOT null)
            FROM "{0}";
            """.format(model._meta.db_table)

        with connection.cursor() as cursor:
            cursor.execute(sentence)
            cursor.fetchall()
