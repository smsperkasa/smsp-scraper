import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
import datetime
import json
import base64
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    # Step 1: Load USD to IDR exchange rate from JSON
    logger.info("Loading USD to IDR exchange rate data from JSON")
    with open('usd_to_idr.json', 'r') as file:
        usd_idr_data = json.load(file)
    
    # Extract timestamps and values from the JSON data
    timestamps = usd_idr_data['chart']['result'][0]['timestamp']
    values = usd_idr_data['chart']['result'][0]['indicators']['quote'][0]['close']
    
    # Create a DataFrame for USD to IDR data
    usd_idr_df = pd.DataFrame({
        'time': timestamps,
        'value': values,
        'source': 'USD',
        'target': 'IDR'
    })
    
    # Convert Unix timestamp to datetime
    usd_idr_df['time'] = pd.to_datetime(usd_idr_df['time'], unit='s').dt.normalize()
    usd_idr_df.rename(columns={'time': 'as_of', 'value': 'exchange_rate'}, inplace=True)
    
    # Save USD to IDR data to CSV
    usd_idr_df.to_csv('usd_to_idr_processed.csv', index=False)
    logger.info("USD to IDR data processed and saved to CSV")
    
    # Step 2: Load CNY to IDR exchange rate from CSV
    logger.info("Loading CNY to IDR exchange rate data from CSV")
    cny_idr_df = pd.read_csv('cny_to_idr.csv')
    
    # Rename and select columns to match the format
    cny_idr_df = cny_idr_df[['as_of', 'cny_to_idr']]
    cny_idr_df.rename(columns={'cny_to_idr': 'exchange_rate'}, inplace=True)
    cny_idr_df['source'] = 'CNY'
    cny_idr_df['target'] = 'IDR'
    
    # Convert 'as_of' to datetime
    cny_idr_df['as_of'] = pd.to_datetime(cny_idr_df['as_of']).dt.strftime('%Y-%m-%d')
    
    # Combine both DataFrames
    combined_df = pd.concat([usd_idr_df, cny_idr_df], ignore_index=True)
    
    # Sort by date and currency pair
    combined_df = combined_df.sort_values(by=['as_of', 'source'])
    
    # Step 3: Prepare data for Snowflake
    # Format the dataframe according to the CURRENCIES table structure
    snowflake_df = pd.DataFrame({
        'AS_OF': pd.to_datetime(combined_df['as_of']).dt.strftime('%Y-%m-%d %H:%M:%S'),
        'CURRENCY_EXCHANGE': combined_df.apply(lambda row: f"{row['source']}/IDR", axis=1),
        'VALUE': combined_df['exchange_rate'],
        'SOURCE': 'Yahoo Finance'
    })
    
    # Print dataframe information for debugging
    logger.info(f"DataFrame columns: {snowflake_df.columns.tolist()}")
    logger.info(f"DataFrame shape: {snowflake_df.shape}")
    logger.info(f"AS_OF column data type: {snowflake_df['AS_OF'].dtype}")
    logger.info(f"First few AS_OF values: {snowflake_df['AS_OF'].head().tolist()}")
    
    # Load the private key for Snowflake connection
    logger.info("Loading private key for Snowflake connection")
    with open("rsa_key.pem", "rb") as key:
        p_key = serialization.load_pem_private_key(
            key.read(),
            password=None,
        )

    # Convert the private key to DER format and then base64 encode it
    pkb = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Base64 encode the DER formatted key
    pkb_base64 = base64.b64encode(pkb).decode('utf-8')
    
    # Snowflake connection details
    snowflake_user = 'TEDDYSMSPERKASA'
    snowflake_account = 'xqkrxeb-it68965'
    snowflake_database = 'RAW'
    snowflake_schema = 'EXTERNAL_INDICATORS'
    snowflake_warehouse = 'SMSP_WH'

    # Connect to Snowflake
    logger.info("Connecting to Snowflake")
    conn = snowflake.connector.connect(
        user=snowflake_user,
        account=snowflake_account,
        private_key=pkb_base64,
        warehouse=snowflake_warehouse,
        database=snowflake_database,
        schema=snowflake_schema      
    )
    
    logger.info("Connected to Snowflake successfully")

    # Create a cursor
    cur = conn.cursor()

    # Step 4: Create a temporary staging table
    temp_table_name = 'TEMP_CURRENCIES'
    create_temp_table_query = f"""
    CREATE OR REPLACE TEMPORARY TABLE {temp_table_name} (
        "AS_OF" TIMESTAMP_NTZ,
        "CURRENCY_EXCHANGE" VARCHAR,
        "VALUE" FLOAT,
        "SOURCE" VARCHAR
    );
    """
    cur.execute(create_temp_table_query)
    logger.info(f"Temporary table {temp_table_name} created")

    # Step 5: Upload the data to the temporary table
    logger.info("Uploading data to temporary table...")
    success, num_chunks, num_rows, output = write_pandas(
        conn=conn,
        df=snowflake_df,
        table_name=temp_table_name,
        database=snowflake_database,
        schema=snowflake_schema,
        quote_identifiers=True
    )
    logger.info(f"Data upload status: {success}, Rows uploaded: {num_rows}")

    # Step 6: Use MERGE to handle overlaps
    target_table_name = 'CURRENCIES'
    merge_query = f"""
    MERGE INTO {target_table_name} AS target
    USING {temp_table_name} AS source
    ON target."AS_OF" = source."AS_OF" AND target."CURRENCY_EXCHANGE" = source."CURRENCY_EXCHANGE"
    WHEN MATCHED THEN
        UPDATE SET target."VALUE" = source."VALUE", target."SOURCE" = source."SOURCE"
    WHEN NOT MATCHED THEN
        INSERT ("AS_OF", "CURRENCY_EXCHANGE", "VALUE", "SOURCE")
        VALUES (source."AS_OF", source."CURRENCY_EXCHANGE", source."VALUE", source."SOURCE");
    """
    cur.execute(merge_query)
    logger.info("Merge completed")

    # Commit the transaction
    conn.commit()
    logger.info("Transaction committed")
    
    # Close the cursor
    cur.close()

    logger.info("Data has been successfully uploaded to Snowflake without overlaps.")
except Exception as e:
    logger.error(f"Connection failed: {e}")
    
    # Check for common errors and provide troubleshooting guidance
    if "does not exist" in str(e):
        logger.error("TROUBLESHOOTING: The table cannot be found. This could be due to:")
        logger.error("- Incorrect table name case (Snowflake table names are case-sensitive)")
        logger.error("- Issues with table creation or write_pandas operation")
        logger.error("- Session or transaction timing out")
    elif "invalid identifier" in str(e):
        logger.error("TROUBLESHOOTING: Invalid identifier detected. This could be due to:")
        logger.error("- Column names need to be properly quoted in SQL statements")
        logger.error("- Case-sensitivity issues with column names")
        logger.error("- Mismatch between DataFrame column names and SQL column names")
    elif "Failed to cast variant value" in str(e):
        logger.error("TROUBLESHOOTING: Data type conversion error. This could be due to:")
        logger.error("- Date format issues - ensure dates are in YYYY-MM-DD format")
        logger.error("- Numeric format issues")
        logger.error("- Incompatible data types between DataFrame and Snowflake table")
    elif "Failed to decode private key" in str(e):
        logger.error("TROUBLESHOOTING: Private key format error. This could be due to:")
        logger.error("- Incorrect private key format (needs to be base64-encoded DER format)")
        logger.error("- Issues with the private key file")
finally:
    # Make sure the connection is properly closed
    try:
        if 'conn' in locals() and conn is not None:
            conn.close()
            logger.info("Connection closed")
    except Exception as close_error:
        logger.error(f"Error closing connection: {close_error}") 