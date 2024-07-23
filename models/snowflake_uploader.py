from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine

from config import ACCOUNT, PASSWORD, USER, WAREHOUSE
from logger.logging_config import logger


class SnowflakeUploader:
    def upload_data_to_snowflake(self, database, schema, table, df):  # pragma: no cover
        """
        Utility: Uploads df to Snowflake, specifies database, schema, and table
        """
        url_post = URL(
            account=ACCOUNT,
            user=USER,
            password=PASSWORD,
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
        except:
            logger.warning("Cannot upload to Snowflake")
