from sqlalchemy.engine import URL, create_engine
import pandas as pd
import struct
from azure.identity import DefaultAzureCredential

query_path = "./get_names_for_dropdowns.sql"


def get_conn():
    conn_str = (
        "driver={ODBC Driver 17 for SQL Server};"
        "server=tcp:ods-sql-server-us.database.windows.net;"
        "database=salesops-sql-prod-us;"
        "encrypt=yes;"
        "trustservercertificate=no;"
        "connection timeout=30"
    )
    credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)
    token = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
    token_struct = struct.pack(f'<I{len(token)}s', len(token), token)
    connection_url = URL.create("mssql+pyodbc",
                                query={"odbc_connect": conn_str})
    engine = create_engine(connection_url,
                           connect_args={"attrs_before": {1256: token_struct}})
    return engine


with get_conn().connect() as conn:
    with open(query_path) as sql:
        query = sql.read()
    df = pd.read_sql_query(query, conn)
pd.DataFrame(df).to_excel("names.xlsx", index=False)
