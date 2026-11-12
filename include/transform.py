
import os
import polars as pl

from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient


# Load environment variables
load_dotenv()

ACCOUNT_NAME = "urbancitystorage1"


def transform():

    # Define Azure Bronze and Silver file paths
    source_uri = "az://bronze/urban_service_requests.csv"
    target_uri = "az://silver/urban_service_requests.parquet"

    # Retrieve the Azure Storage account key
    account_key = os.getenv("ACCOUNT_KEY")

    if not account_key:
        raise ValueError("ACCOUNT_KEY environment variable is missing.")

    # Configure Azure Storage access for Polars
    storage_options = {
        "account_name": ACCOUNT_NAME,
        "account_key": account_key
    }

    # Connect to Azure Blob Storage
    blob_service = BlobServiceClient(
        account_url=f"https://{ACCOUNT_NAME}.blob.core.windows.net",
        credential=account_key
    )

    # Reference the existing Silver Parquet file
    silver_blob = blob_service.get_blob_client(
        container="silver",
        blob="urban_service_requests.parquet"
    )

    # Skip transformation if Silver file already exists
    if silver_blob.exists():
        print("Silver Parquet already exists. Skipping transformation.")
        return None

    print("Starting Bronze-to-Silver transformation...")

    # Read the raw CSV from Azure Bronze
    df = pl.scan_csv(
        source_uri,
        storage_options=storage_options
    )

    # Rename and select the required columns
    column_mapping = {
        "Created Date": "created_date",
        "Closed Date": "closed_date",
        "Problem (formerly Complaint Type)": "problem",
        "Problem Detail (formerly Descriptor)": "problem_detail",
        "Location Type": "location_type",
        "Incident Address": "incident_address",
        "City": "city",
        "Borough": "borough",
        "Latitude": "latitude",
        "Longitude": "longitude"
    }

    df_refined = df.select([
        pl.col(old).alias(new)
        for old, new in column_mapping.items()
    ])

    # Write transformed data to Azure Silver as Parquet
    df_refined.sink_parquet(
        target_uri,
        storage_options=storage_options,
        compression="snappy"
    )

    print(f"Data loaded to {target_uri}")

    return None


# Execute only when this script is run directly
if __name__ == "__main__":
    transform()
