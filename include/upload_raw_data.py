import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from pathlib import Path

location = Path(__file__).resolve().parent
project_root = location.parent

load_dotenv()

ACCOUNT_KEY = os.getenv("ACCOUNT_KEY")
ACCOUNT_NAME = "urbancitystorage1"
CONTAINER_NAME = "bronze"

LOCAL_FILE_PATH = project_root / "data" / "urban_service_requests.csv"
BLOB_NAME = "urban_service_requests.csv"


def upload_data():
    try:
        blob_service_client = BlobServiceClient(
            account_url=f"https://{ACCOUNT_NAME}.blob.core.windows.net",
            credential=ACCOUNT_KEY
        )

        blob_client = blob_service_client.get_blob_client(
            container=CONTAINER_NAME,
            blob=BLOB_NAME
        )

        # Avoid uploading the same file again
        if blob_client.exists():
            print(f"File already exists in {CONTAINER_NAME}. Skipping upload.")
            return None

        print(f"Starting file upload from {LOCAL_FILE_PATH}")

        with open(LOCAL_FILE_PATH, "rb") as data:
            blob_client.upload_blob(
                data,
                overwrite=False,
                max_concurrency=4
            )

        print(f"Upload successful. File loaded to {CONTAINER_NAME}")

    except Exception as e:
        print(f"Upload failed: {e}")
        raise

    return None


if __name__ == "__main__":
    upload_data()
