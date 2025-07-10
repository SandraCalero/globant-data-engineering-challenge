import boto3
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class S3Service:
    @staticmethod
    def list_csv_files(bucket_name: str) -> List[str]:
        """List all CSV files in the given S3 bucket."""
        logger.info(f"Listing CSV files in bucket: {bucket_name}")
        s3 = boto3.client('s3')
        response = s3.list_objects_v2(Bucket=bucket_name)
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                if key.endswith('.csv'):
                    files.append(key)
        logger.info(f"Found {len(files)} CSV files in bucket '{bucket_name}'")
        return files

    @staticmethod
    def read_csv_file(bucket_name: str, key: str) -> List[List[str]]:
        """Read a CSV file from S3 and return a list of rows (each row is a list of strings)."""
        logger.info(f"Reading CSV file from bucket: {bucket_name}, key: {key}")
        s3 = boto3.client('s3')
        file_obj = s3.get_object(Bucket=bucket_name, Key=key)
        content = file_obj['Body'].read().decode('utf-8')
        # Split into rows and columns (no header)
        rows = [line.strip().split(',')
                for line in content.strip().splitlines() if line.strip()]
        logger.info(
            f"Read {len(rows)} rows from file '{key}' in bucket '{bucket_name}'")
        return rows


class DatabaseService:
    @staticmethod
    def batch_upsert(table_name: str, bucket_name: str, csv_filename: str, session, model_class, batch_size: int = 1000) -> Dict[str, Any]:
        """
        Insert or update rows in batches. If id exists, update; else insert. Returns a summary.
        """
        files = S3Service.list_csv_files(bucket_name)
        if csv_filename not in files:
            error_msg = f"{csv_filename} not found in S3 bucket"
            logger.error(error_msg)
            return {
                "table": table_name,
                "error": error_msg,
                "total": 0,
                "inserted": 0,
                "updated": 0,
                "failed": 0,
                "errors": []
            }

        rows = S3Service.read_csv_file(bucket_name, csv_filename)

        logger.info(
            f"Starting batch upsert for table '{table_name}' with {len(rows)} rows (batch size: {batch_size})")

        total = len(rows)
        inserted = 0
        updated = 0
        failed = 0
        errors = []

        for batch_start in range(0, total, batch_size):
            batch = rows[batch_start:batch_start+batch_size]
            logger.info(
                f"Processing batch {batch_start//batch_size + 1}: {len(batch)} rows")

            # Process entire batch in a single transaction
            try:
                batch_inserted = 0
                batch_updated = 0

                for row in batch:
                    try:
                        # Build dict from model fields and row values
                        field_names = list(model_class.model_fields.keys())
                        # Validate data using the model class
                        validated_data = model_class.model_validate(
                            dict(zip(field_names, row)))
                        # Check if id exists
                        obj = session.get(model_class, validated_data.id)
                        if obj:
                            validated_dict = validated_data.model_dump(
                                exclude_unset=True, exclude={'id'})
                            obj.sqlmodel_update(validated_dict)
                            session.add(obj)
                            batch_updated += 1
                        else:
                            session.add(validated_data)
                            batch_inserted += 1
                    except Exception as e:
                        failed += 1
                        errors.append({"row": row, "error": str(e)})

                # Commit the entire batch
                session.commit()
                inserted += batch_inserted
                updated += batch_updated
                logger.info(
                    f"Batch {batch_start//batch_size + 1} committed: {batch_inserted} inserted, {batch_updated} updated")

            except Exception as e:
                # Rollback the entire batch if there's an error
                session.rollback()
                logger.error(
                    f"Batch {batch_start//batch_size + 1} failed and rolled back: {e}")
                # Count all rows in this batch as failed
                failed += len(batch)
                for row in batch:
                    errors.append({"row": row, "error": f"Batch failed: {e}"})

        logger.info(
            f"Batch upsert completed for table '{table_name}'. Inserted: {inserted}, Updated: {updated}, Failed: {failed}")
        return {
            "table": table_name,
            "total": total,
            "inserted": inserted,
            "updated": updated,
            "failed": failed,
            "errors": errors
        }
