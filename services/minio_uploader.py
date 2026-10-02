import os
from services.minio_factory import get_minio_service

def upload_excel_report(file_path: str, month_year: str, version_name: str) -> bool:
    try:
        minio_service = get_minio_service()
        file_name = f"{version_name}.xlsx"
        month, year = month_year[:2], month_year[2:]
        minio_path = f"{year}/{year}{month}/{file_name}"

        with open(file_path, 'rb') as file_data:
            file_stat = os.stat(file_path)
            minio_service.client.put_object(
                bucket_name='tbg-reports',
                object_name=minio_path,
                data=file_data,
                length=file_stat.st_size,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        print(f"\n✅ File uploaded to MinIO: {minio_service.bucket_name}/{minio_path}")
        return True

    except Exception as e:
        print(f"\n❌ Error uploading to MinIO: {str(e)}")
        return False
