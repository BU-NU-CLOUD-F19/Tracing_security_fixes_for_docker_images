import psycopg2
from config import config
import pandas as pd

class PostgresOps:
    def __init__(self, packages):
        self.packages = packages
        self.conn = None

    def connect(self):
        """ Connect to the PostgreSQL database server """
        try:
            # read connection parameters
            params = config()

            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            self.conn = psycopg2.connect(**params)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def get_clair_reports(self):

        # create a cursor
        if self.conn:
            cur = self.conn.cursor()
        else:
            raise ValueError("Make DB connection first.")

        valid_packages = ', '.join("'{0}'".format(p) for p in self.packages)
        reports_data = []

        # execute a statement
        for package in valid_packages.split(", "):
            query = "select f.name, v.name, n.name, fix.version from vulnerability_fixedin_feature fix, feature f, " \
                    "vulnerability v, namespace n where fix.feature_id = f.id and v.id = fix.vulnerability_id and " \
                    "f.namespace_id = n.id and f.name = " + package + ";"
            try:
                cur.execute(query)
                print("Package:", package)
                result_set = cur.fetchall()
                if result_set:
                    for result in result_set:
                        reports_data.append(list(result))

            except(Exception, psycopg2.DatabaseError) as error:
                print(error)

        if self.conn is not None:
            self.conn.close()
            print('Database connection closed.')
            # close the communication with the PostgreSQL
        cur.close()

        clair_db_reports = pd.DataFrame(reports_data, columns=["Package", "Vulnerability",
                                             "OS", "Package_Version"])
        clair_db_reports.reset_index(inplace=True)
        return clair_db_reports



# if __name__ == '__main__':
#     post = PostgresOps({})
#     post.connect()
