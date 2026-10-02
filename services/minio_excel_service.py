from minio import Minio
from io import BytesIO
import pandas as pd

class MinIOExcelService:
    def __init__(self, endpoint, access_key, secret_key, bucket_name, secure=True, http_client=None):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
            http_client=http_client  # Optional, for disabling cert verification in test
        )
        self.bucket_name = bucket_name

    def read_excel(self, object_name, **kwargs):  # Accept all extra keyword args
        response = self.client.get_object(self.bucket_name, object_name)
        return pd.read_excel(BytesIO(response.read()), engine="openpyxl", **kwargs)

    def get_file_bytes(self, object_name):
        response = self.client.get_object(bucket_name=self.bucket_name, object_name=object_name)
        return response.read()
