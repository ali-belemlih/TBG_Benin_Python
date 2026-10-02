import os
import urllib3
from dotenv import load_dotenv
from services.minio_excel_service import MinIOExcelService

load_dotenv()

def get_minio_service(bucket_name=None):
    # Get optional custom CA cert path from env
    custom_cert_path = os.getenv("MINIO_CA_CERT")

    if os.getenv("ENV", "").lower() in {"test", "dev"} or os.getenv("MINIO_SKIP_CERT_VERIFY") == "1":
        # Insecure: skip certificate verification
        http_client = urllib3.PoolManager(cert_reqs='CERT_NONE')

    elif custom_cert_path:
        # Secure: trust the provided CA certificate
        http_client = urllib3.PoolManager(
            cert_reqs='CERT_REQUIRED',
            ca_certs=custom_cert_path
        )
    return MinIOExcelService(
        endpoint=os.getenv("MINIO_ENDPOINT"),
        access_key=os.getenv("MINIO_ACCESS_KEY"),
        secret_key=os.getenv("MINIO_SECRET_KEY"),
        bucket_name=bucket_name or os.getenv("MINIO_BUCKET_NAME", "tbg-automation-files"),
        secure=True,
        http_client=http_client
    )
