import boto3
import csv
import logging
import os
from botocore.exceptions import ClientError
from io import StringIO

from .models import BatchResponse

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000


class S3Service:
    """
    Service class for interacting with AWS S3, including bucket validation,
    listing CSV files, and reading CSV file contents for migration operations.
    """
    @staticmethod
    def get_and_validate_s3_bucket_name() -> str:
        """Validate that S3_BUCKET_NAME environment variable is set."""
        try:
            bucket_name = os.getenv("S3_BUCKET_NAME")
            if not bucket_name:
                raise ValueError(
                    "S3_BUCKET_NAME environment variable is not set")
            s3 = boto3.client('s3')
            s3.head_bucket(Bucket=bucket_name)
            return bucket_name

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.error(f"Bucket '{bucket_name}' not found")
                raise FileNotFoundError(f"Bucket '{bucket_name}' not found")
            else:
                logger.error(f"AWS ClientError validating bucket: {e}")
                raise
        except Exception as e:
            logger.error(
                f"Unexpected error validating bucket '{bucket_name}': {e}")
            raise

    @staticmethod
    def list_csv_files(bucket_name: str, prefix: str | None = None) -> list[str]:
        """List CSV files in the given S3 bucket, optionally filtered by prefix."""
        try:
            logger.info(f"Listing CSV files in bucket: {bucket_name}" + (
                f" with prefix: {prefix}" if prefix else ""))
            s3 = boto3.client('s3')

            if prefix:
                response = s3.list_objects_v2(
                    Bucket=bucket_name, Prefix=prefix)
            else:
                response = s3.list_objects_v2(Bucket=bucket_name)

            files = [obj['Key'] for obj in response.get(
                'Contents', []) if obj['Key'].endswith('.csv')]

            if len(files) == 0:
                logger.warning(f"No CSV files found in bucket '{bucket_name}'" +
                               (f" with prefix '{prefix}'" if prefix else ""))

            logger.info(f"Found {len(files)} CSV files in bucket '{bucket_name}'" +
                        (f" with prefix '{prefix}'" if prefix else ""))
            return files

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchBucket':
                logger.error(f"Bucket '{bucket_name}' not found")
                raise FileNotFoundError(f"Bucket '{bucket_name}' not found")
            else:
                logger.error(f"AWS ClientError: {e}")
                raise
        except Exception as e:
            logger.error(
                f"Error listing files in bucket '{bucket_name}': {str(e)}")
            raise

    @staticmethod
    def read_csv_file(bucket_name: str, key: str) -> list[list[str]]:
        """Read a CSV file from S3 and return a list of rows (each row is a list of strings)."""
        logger.info(f"Reading CSV file from bucket: {bucket_name}, key: {key}")
        s3 = boto3.client('s3')
        try:
            file_obj = s3.get_object(Bucket=bucket_name, Key=key)
            content = file_obj['Body'].read().decode('utf-8')

            # Split into rows and columns (no header)
            rows = list(csv.reader(StringIO(content)))
            logger.info(f"Read {len(rows)} rows from file '{key}'")

            return rows

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                logger.error(
                    f"File '{key}' not found in bucket '{bucket_name}'")
                raise FileNotFoundError(
                    f"File '{key}' not found in bucket '{bucket_name}'")
            elif error_code == 'NoSuchBucket':
                logger.error(f"Bucket '{bucket_name}' not found")
                raise FileNotFoundError(f"Bucket '{bucket_name}' not found")
            else:
                logger.error(f"AWS ClientError: {e}")
                raise
        except Exception as e:
            logger.error(
                f"Error reading file '{key}' from bucket '{bucket_name}': {str(e)}")
            raise


class DatabaseService:
    """
    Service class for handling database operations related to batch upserts,
    row validation, and error handling for migration processes.
    """
    @staticmethod
    def _clean_row_data(row: list) -> list:
        """Clean row data by converting empty strings to None."""
        return [
            None if (isinstance(value, str) and value.strip() == "") or value == "" or value is None
            else value
            for value in row
        ]

    @staticmethod
    def _process_single_row(session, model_class, field_names: list, row: list) -> tuple[int, int, list]:
        """Process a single row and return (inserted, updated, errors)."""
        try:

            # Validate data using the model class
            cleaned_row = DatabaseService._clean_row_data(row)
            validated_data = model_class.model_validate(
                dict(zip(field_names, cleaned_row)))
            # Check if id exists
            obj = session.get(model_class, validated_data.id)
            if obj:
                validated_dict = validated_data.model_dump(
                    exclude_unset=True, exclude={'id'})
                obj.sqlmodel_update(validated_dict)
                session.add(obj)
                return 0, 1, []  # updated
            else:
                session.add(validated_data)
                return 1, 0, []  # inserted

        except Exception as e:
            # failed
            return 0, 0, [{"row": row, "error": str(e)}]

    @staticmethod
    def _process_batch(session, model_class, field_names: list, batch: list, batch_num: int) -> tuple[int, int, int, list]:
        """Process a batch of rows and return (inserted, updated, failed, errors)."""
        batch_inserted = batch_updated = batch_failed = 0
        batch_errors = []

        try:
            for row in batch:
                inserted, updated, errors = DatabaseService._process_single_row(
                    session, model_class, field_names, row
                )
                batch_inserted += inserted
                batch_updated += updated
                batch_errors.extend(errors)
                if errors:
                    batch_failed += 1

            session.commit()
            logger.info(
                f"Batch {batch_num}' committed: {batch_inserted} inserted, {batch_updated} updated")

        except Exception as e:
            session.rollback()
            logger.error(
                f"Batch {batch_num}' failed and rolled back: {e}")
            batch_failed = len(batch)
            batch_errors = [{"rows_affected": len(
                batch), "error": f"Batch failed: {e}"}]
            batch_inserted = batch_updated = 0

        return batch_inserted, batch_updated, batch_failed, batch_errors

    @staticmethod
    def _process_file(session, model_class, field_names: list, csv_file: str, bucket_name: str) -> tuple[int, int, int, int, list]:
        """Process a single CSV file and return (total, inserted, updated, failed, errors, processed_files)."""
        try:
            logger.info(f"Processing file: {csv_file}")
            rows = S3Service.read_csv_file(bucket_name, csv_file)

            file_total = len(rows)
            file_inserted = file_updated = file_failed = 0
            file_errors = []

            logger.info(
                f"Starting batch upsert for file '{csv_file}' with {file_total} rows (batch size: {BATCH_SIZE})")

            for batch_start in range(0, file_total, BATCH_SIZE):
                batch = rows[batch_start:batch_start+BATCH_SIZE]
                batch_num = batch_start//BATCH_SIZE + 1

                logger.info(
                    f"Processing batch {batch_num} for file '{csv_file}': {len(batch)} rows")

                batch_inserted, batch_updated, batch_failed, batch_errors = DatabaseService._process_batch(
                    session, model_class, field_names, batch, batch_num
                )

                file_inserted += batch_inserted
                file_updated += batch_updated
                file_failed += batch_failed
                file_errors.extend(batch_errors)

            logger.info(
                f"File '{csv_file}' completed. Inserted: {file_inserted}, Updated: {file_updated}, Failed: {file_failed}")
            return file_total, file_inserted, file_updated, file_failed, file_errors

        except FileNotFoundError as e:
            logger.error(f"File '{csv_file}' not found: {str(e)}")
            return 0, 0, 0, 1, [{"file": csv_file, "file_error": str(e)}]
        except Exception as e:
            logger.error(f"Error processing file '{csv_file}': {str(e)}")
            return 0, 0, 0, 1, [{"file": csv_file, "file_error": str(e)}]

    @staticmethod
    def batch_upsert(session, model_class) -> BatchResponse:
        """
        Insert or update rows in batches. If id exists, update; else insert. Returns a summary.
        """
        bucket_name = S3Service.get_and_validate_s3_bucket_name()
        table_name = None
        total = inserted = updated = failed = 0
        errors = []
        processed_files = []
        try:
            table_name = model_class.__name__.lower()
            prefix = f"{model_class.__name__}/"
            field_names = list(model_class.model_fields.keys())

            # Get CSV files for the model
            csv_files = S3Service.list_csv_files(bucket_name, prefix)

            if len(csv_files) == 0:
                raise ValueError(
                    f"No CSV files found for folder '{prefix}'")
                # Process all files
            for csv_file in csv_files:
                file_total, file_inserted, file_updated, file_failed, file_errors = DatabaseService._process_file(
                    session, model_class, field_names, csv_file, bucket_name
                )
                total += file_total
                inserted += file_inserted
                updated += file_updated
                failed += file_failed
                errors.extend(file_errors)
                processed_files.append(csv_file)

            logger.info(
                f"Batch upsert completed for table '{table_name}'. Processed {len(processed_files)} files. Total: {total}, Inserted: {inserted}, Updated: {updated}, Failed: {failed}")
        except Exception as e:
            logger.error(f"Error during batch upsert: {str(e)}")
            errors.append({"error": str(e)})

        return BatchResponse(
            table=table_name,
            total=total,
            inserted=inserted,
            updated=updated,
            failed=failed,
            errors=errors,
            processed_files=processed_files
        )
