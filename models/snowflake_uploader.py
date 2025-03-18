from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
import base64

from config import ACCOUNT, PRIVATE_KEY_PATH, USER, WAREHOUSE
from logger.logging_config import logger
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption

class SnowflakeUploader:
    def upload_data_to_snowflake(self, database, schema, table, df):  # pragma: no cover
        """
        Utility: Uploads df to Snowflake, specifies database, schema, and table
        """
        
        try:
            #load private key
            with open(PRIVATE_KEY_PATH, "rb") as key:
                p_key = serialization.load_pem_private_key(
                    key.read(),
                    password=None,
                )

            # Convert to DER format and then base64 encode
            pkb = p_key.private_bytes(
                encoding=Encoding.DER,
                format=PrivateFormat.PKCS8,
                encryption_algorithm=NoEncryption()
            )
            pkb_base64 = base64.b64encode(pkb).decode('utf-8')
            
            url_post = URL(
                account=ACCOUNT,
                user=USER,
                private_key=pkb_base64,
                warehouse=WAREHOUSE,
                database=database,
            )

            engine_post = create_engine(url_post)
            with engine_post.begin() as conn:
                df.to_sql(
                    table, con=conn, schema=schema, if_exists="append", index=False
                )
            logger.info("Uploaded to Snowflake successfully")
        except Exception as e:
            logger.error(f"Failed to upload to Snowflake: {str(e)}")
            logger.warning("Cannot upload to Snowflake")
