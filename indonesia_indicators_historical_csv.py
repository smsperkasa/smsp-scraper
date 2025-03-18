import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from cryptography.hazmat.primitives import serialization
import datetime
import json
import csv

try:
    #First, load the External Indicators - indonesia_indicators.csv
    df = pd.read_csv('External Indicators - indonesia_indicator.csv')
    
    #remove the #N/A values in the value column
    df = df[df['VALUE'] != '#N/A']

    # Convert the 'as_of' column to a datetime object
    df['AS_OF'] = pd.to_datetime(df['AS_OF']).dt.strftime('%Y-%m-%d')   
    
    #uppercase the df columns
    df.columns = df.columns.str.upper()
    
    #Second, connect to snowflake
    # Load the private key
    with open("rsa_key.pem", "rb") as key:
     p_key = serialization.load_pem_private_key(
        key.read(),
        password=None,
     )

    pkb = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    
    # Print dataframe information for debugging
    print(f"DataFrame columns: {df.columns.tolist()}")
    print(f"DataFrame shape: {df.shape}")
    print(f"AS_OF column data type: {df['AS_OF'].dtype}")
    print(f"First few AS_OF values: {df['AS_OF'].head().tolist()}")
    
    # Snowflake connection details
    snowflake_user = 'TEDDYSMSPERKASA'
    snowflake_account = 'xqkrxeb-it68965'
    snowflake_database = 'RAW'
    snowflake_schema = 'EXTERNAL_INDICATORS'
    snowflake_warehouse = 'SMSP_WH'

    # Connect to Snowflake
    conn = snowflake.connector.connect(
        user=snowflake_user,
        account=snowflake_account,
        private_key=pkb,
        warehouse=snowflake_warehouse,
        database=snowflake_database,
        schema=snowflake_schema      
    )
    
    print("Connected to Snowflake successfully")

    # Create a cursor
    cur = conn.cursor()

    # Step 1: Create a temporary staging table
    temp_table_name = 'TEMP_INDONESIA_INDICATORS'  # Use uppercase for table names
    create_temp_table_query = f"""
    CREATE OR REPLACE TEMPORARY TABLE {temp_table_name} (
        "AS_OF" DATE,
        "VALUE" FLOAT,
        "SOURCE" VARCHAR,
        "UNIT" VARCHAR,
        "TYPE" VARCHAR
    );
    """
    cur.execute(create_temp_table_query)
    print(f"Temporary table {temp_table_name} created")

    # Step 2: Upload the CSV data to the temporary table
    # Convert DataFrame to dictionary to control data types
    # write_pandas will automatically handle the data type conversions
    print("Uploading data to temporary table...")
    success, num_chunks, num_rows, output = write_pandas(
        conn=conn,
        df=df,
        table_name=temp_table_name,
        database=snowflake_database,
        schema=snowflake_schema,
        quote_identifiers=True
    )
    print(f"Data upload status: {success}, Rows uploaded: {num_rows}")

    # Step 3: Use MERGE to handle overlaps, include all the df columns in the insert statement
    target_table_name = 'INDONESIA_INDICATORS'  # Use uppercase for table names
    merge_query = f"""
    MERGE INTO {target_table_name} AS target
    USING {temp_table_name} AS source
    ON target."AS_OF" = source."AS_OF"
    WHEN MATCHED THEN
        UPDATE SET target."VALUE" = source."VALUE"
    WHEN NOT MATCHED THEN
        INSERT ("AS_OF", "VALUE", "SOURCE", "UNIT", "TYPE")
        VALUES (source."AS_OF", source."VALUE", source."SOURCE", source."UNIT", source."TYPE");
    """
    cur.execute(merge_query)
    print("Merge completed")

   
    cur.execute(merge_query)
    normalized_rows = cur.rowcount
    print(f"Price normalization completed. {normalized_rows} rows updated.")

    # Commit the transaction
    conn.commit()
    print("Transaction committed")
    
    # Close the cursor
    cur.close()

    print("Data has been successfully uploaded to Snowflake without overlaps.")
except Exception as e:
    print(f"Connection failed: {e}")
    
    # Check if it's a specific error about the table
    if "does not exist" in str(e):
        print("TROUBLESHOOTING: The temporary table cannot be found. This could be due to:")
        print("- Incorrect table name case (Snowflake table names are case-sensitive)")
        print("- Issues with table creation or write_pandas operation")
        print("- Session or transaction timing out")
    elif "invalid identifier" in str(e):
        print("TROUBLESHOOTING: Invalid identifier detected. This could be due to:")
        print("- Column names need to be properly quoted in SQL statements")
        print("- Case-sensitivity issues with column names")
        print("- Mismatch between DataFrame column names and SQL column names")
    elif "Failed to cast variant value" in str(e):
        print("TROUBLESHOOTING: Data type conversion error. This could be due to:")
        print("- Date format issues - ensure dates are in YYYY-MM-DD format")
        print("- Numeric format issues")
        print("- Incompatible data types between DataFrame and Snowflake table")
finally:
    # Make sure the connection is properly closed
    try:
        if 'conn' in locals() and conn is not None:
            conn.close()
            print("Connection closed")
    except Exception as close_error:
        print(f"Error closing connection: {close_error}")

