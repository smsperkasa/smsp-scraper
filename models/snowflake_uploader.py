from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine

from config import ACCOUNT, PRIVATE_KEY_PATH, USER, WAREHOUSE
from logger.logging_config import logger
from cryptography.hazmat.primitives import serialization

class SnowflakeUploader:
    def upload_data_to_snowflake(self, database, schema, table, df):  # pragma: no cover
        """
        Utility: Uploads df to Snowflake, specifies database, schema, and table
        """
        
        #load private key
        with open(PRIVATE_KEY_PATH, "rb") as key:
            p_key = serialization.load_pem_private_key(
                key.read(),
                password=None,
            )

        pkb = p_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        url_post = URL(
            account=ACCOUNT,
            user=USER,
            private_key=pkb,
            warehouse=WAREHOUSE,
            database=database,
        )

        try:
            engine_post = create_engine(url_post)
            with engine_post.begin() as conn:
                df.to_sql(
                    table, con=conn, schema=schema, if_exists="append", index=False
                )
            logger.info("Uploaded to Snowflake successfully")
        except Exception as e:
            print(e)
            logger.warning("Cannot upload to Snowflake")
