import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from cryptography.hazmat.primitives import serialization
import datetime
import json
import csv

try:
    #First, load the cny to idr exchange rate
    # Load JSON data into a Pandas DataFrame
    df = pd.read_json('cny_to_idr.json')

    # Convert the 'time' column from milliseconds to Unix timestamp (seconds)
    df['time'] = df['time'] / 1000

    # Convert the Unix timestamp to a human-readable format
    df['time_human_readable'] = pd.to_datetime(df['time'], unit='s').dt.normalize()
    
    #rename the time_human_readable to as_of, and rename the value to cny_to_idr
    df.rename(columns={'time_human_readable': 'as_of', 'value': 'cny_to_idr'}, inplace=True)
    
    # Save the DataFrame to a CSV file
    df.to_csv('cny_to_idr.csv', index=False)

    print("CSV file has been created at: cny_to_idr.csv")
    
    #Second, merge the cny_to_idr.csv with chinese_rebar_prices.csv
    df_cny_to_idr = pd.read_csv('cny_to_idr.csv')
    df_chinese_rebar_prices = pd.read_csv('chinese_rebar_prices.csv')

    # Merge the two DataFrames on the 'as_of' column
    merged_df = pd.merge(df_chinese_rebar_prices, df_cny_to_idr, on='as_of', how='inner')
    
    #then multiply the value column by the cny_to_idr column, then divide by 1000 to get the idr value per kg
    merged_df['idr_value_per_kg'] = (merged_df['value'] * merged_df['cny_to_idr']) / 1000

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
    
    # Create a new DataFrame instead of modifying a slice to avoid warnings
    # First extract the needed columns
    select_cols = merged_df[['as_of', 'idr_value_per_kg']]
    
    # Create a new DataFrame with the selected columns
    df = pd.DataFrame({
        'as_of': pd.to_datetime(select_cols['as_of']).dt.strftime('%Y-%m-%d'),
        'sku_number': '-',
        'product': "Besi Beton",
        'recorded_by': 'SMSP Scraper',
        'type': 'Competitor',
        'industry': 'Factory',
        'source': 'sina',
        'location': 'China',
        'weight': 0,
        'quantity': 1,
        'price_include_tax_per_kg': select_cols['idr_value_per_kg'],
        'price_include_tax_per_unit': 1,
        'notes': "Scraped by SMSP Scraper"
    })
        
    # Rename columns to uppercase to match Snowflake conventions
    df.columns = [col.upper() for col in df.columns]
    
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
    temp_table_name = 'TEMP_IRON_ORE_DATA'  # Use uppercase for table names
    create_temp_table_query = f"""
    CREATE OR REPLACE TEMPORARY TABLE {temp_table_name} (
        "AS_OF" DATE,
        "IDR_VALUE_PER_KG" FLOAT,
        "SKU_NUMBER" VARCHAR,
        "PRODUCT" VARCHAR,
        "RECORDED_BY" VARCHAR,
        "TYPE" VARCHAR,
        "INDUSTRY" VARCHAR,
        "SOURCE" VARCHAR,
        "LOCATION" VARCHAR,
        "WEIGHT" FLOAT,
        "QUANTITY" FLOAT,
        "PRICE_INCLUDE_TAX_PER_UNIT" FLOAT,
        "PRICE_INCLUDE_TAX_PER_KG" FLOAT,
        "NOTES" VARCHAR
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
    target_table_name = 'CHINESE_REBAR_TRADINGS'  # Use uppercase for table names
    merge_query = f"""
    MERGE INTO {target_table_name} AS target
    USING {temp_table_name} AS source
    ON target."AS_OF" = source."AS_OF"
    WHEN MATCHED THEN
        UPDATE SET target."PRICE_INCLUDE_TAX_PER_KG" = source."PRICE_INCLUDE_TAX_PER_KG"
    WHEN NOT MATCHED THEN
        INSERT ("AS_OF", "SKU_NUMBER", "PRODUCT", "RECORDED_BY", "TYPE", "INDUSTRY", "SOURCE", "LOCATION", "WEIGHT", "QUANTITY", "PRICE_INCLUDE_TAX_PER_UNIT", "PRICE_INCLUDE_TAX_PER_KG", "NOTES")
        VALUES (source."AS_OF", source."SKU_NUMBER", source."PRODUCT", source."RECORDED_BY", source."TYPE", source."INDUSTRY", source."SOURCE", source."LOCATION", source."WEIGHT", source."QUANTITY", source."PRICE_INCLUDE_TAX_PER_UNIT", source."PRICE_INCLUDE_TAX_PER_KG", source."NOTES");
    """
    cur.execute(merge_query)
    print("Merge completed")

    # Step 4: Normalize any existing data where price_include_tax_per_kg is more than 1,000,000
    print("Normalizing existing price data...")
    normalize_price_query = f"""
    UPDATE {target_table_name}
    SET "PRICE_INCLUDE_TAX_PER_KG" = "PRICE_INCLUDE_TAX_PER_KG" / 1000
    WHERE "PRICE_INCLUDE_TAX_PER_KG" > 1000000;
    """
    cur.execute(normalize_price_query)
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

