import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from cryptography.hazmat.primitives import serialization
import datetime

# Connect to Snowflake
try:
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
    
    # Load the CSV file into a DataFrame
    csv_file = 'iron_ore.csv'
    print(f"Reading CSV file: {csv_file}")
    df = pd.read_csv(csv_file)
    
    # Keep only necessary columns and add new ones
    df = df[['as_of', 'value']]  # Keep only these columns
    
    # Make sure as_of is in the correct date format for Snowflake (YYYY-MM-DD)
    # First convert to datetime, then format as string in the expected format
    df['as_of'] = pd.to_datetime(df['as_of']).dt.strftime('%Y-%m-%d')
    
    # Add additional columns
    df["source"] = "sgx.com"
    df["type"] = "IRON ORE CLOSE PRICE"
    df["unit"] = "USD/tonne"
    
    # Rename columns to uppercase to match Snowflake conventions
    df.columns = [col.upper() for col in df.columns]
    
    print(f"DataFrame columns: {df.columns.tolist()}")
    print(f"DataFrame shape: {df.shape}")
    print(f"First row: {df.iloc[0].to_dict()}")
    
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
    temp_table_name = 'TEMP_IRON_ORE_DATA'  # Use uppercase for table names
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

    # Step 3: Use MERGE to handle overlaps
    target_table_name = 'IRON_ORE_INDICATORS'  # Use uppercase for table names
    merge_query = f"""
    MERGE INTO {target_table_name} AS target
    USING {temp_table_name} AS source
    ON target."AS_OF" = source."AS_OF"
    WHEN MATCHED THEN
        UPDATE SET target."VALUE" = source."VALUE"
    WHEN NOT MATCHED THEN
        INSERT ("AS_OF", "VALUE", "SOURCE", "TYPE", "UNIT")
        VALUES (source."AS_OF", source."VALUE", source."SOURCE", source."TYPE", source."UNIT");
    """
    cur.execute(merge_query)
    print("Merge completed")

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

