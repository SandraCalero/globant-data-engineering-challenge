import boto3
import logging

logger = logging.getLogger(__name__)


class S3Service:
    @staticmethod
    def list_csv_files(bucket_name: str, prefix: str = None) -> list[str]:
        """List CSV files in the given S3 bucket, optionally filtered by prefix."""
        logger.info(f"Listing CSV files in bucket: {bucket_name}" + (
            f" with prefix: {prefix}" if prefix else ""))
        s3 = boto3.client('s3')

        if prefix:
            response = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        else:
            response = s3.list_objects_v2(Bucket=bucket_name)

        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                key = obj['Key']
                if key.endswith('.csv'):
                    files.append(key)
        logger.info(f"Found {len(files)} CSV files in bucket '{bucket_name}'" +
                    (f" with prefix '{prefix}'" if prefix else ""))
        return files

    @staticmethod
    def read_csv_file(bucket_name: str, key: str) -> list[list[str]]:
        """Read a CSV file from S3 and return a list of rows (each row is a list of strings)."""
        logger.info(f"Reading CSV file from bucket: {bucket_name}, key: {key}")
        s3 = boto3.client('s3')
        try:
            file_obj = s3.get_object(Bucket=bucket_name, Key=key)
            content = file_obj['Body'].read().decode('utf-8')
            # Split into rows and columns (no header)
            rows = [line.strip().split(',')
                    for line in content.strip().splitlines() if line.strip()]
            logger.info(
                f"Read {len(rows)} rows from file '{key}' in bucket '{bucket_name}'")
            return rows
        except s3.exceptions.NoSuchKey:
            logger.error(f"File '{key}' not found in bucket '{bucket_name}'")
            raise FileNotFoundError(
                f"File '{key}' not found in bucket '{bucket_name}'")
        except s3.exceptions.NoSuchBucket:
            logger.error(f"Bucket '{bucket_name}' not found")
            raise FileNotFoundError(f"Bucket '{bucket_name}' not found")
        except Exception as e:
            logger.error(
                f"Error reading file '{key}' from bucket '{bucket_name}': {str(e)}")
            raise


class DatabaseService:
    @staticmethod
    def batch_upsert(bucket_name: str, session, model_class, batch_size: int = 1000) -> dict[str, any]:
        """
        Insert or update rows in batches. If id exists, update; else insert. Returns a summary.
        """
        # Get table name from model class
        table_name = model_class.__name__.lower()

        # Get folder name (capitalized model class name)
        folder_name = model_class.__name__

        # List CSV files only in the model's folder
        all_files = S3Service.list_csv_files(
            bucket_name, prefix=f"{folder_name}/")

        # Filter only CSV files
        csv_files = [file for file in all_files if file.endswith(".csv")]

        if not csv_files:
            logger.error(
                f"No CSV files found in folder '{folder_name}' for model '{model_class.__name__}'")
            return {
                "table": table_name,
                "total": 0,
                "inserted": 0,
                "updated": 0,
                "failed": 0,
                "errors": [{"file_error": f"No CSV files found in folder '{folder_name}' for model '{model_class.__name__}'"}],
                "file_not_found": True
            }

        # Process all CSV files
        total = 0
        inserted = 0
        updated = 0
        failed = 0
        errors = []
        processed_files = []

        for csv_file in csv_files:
            try:
                logger.info(f"Processing file: {csv_file}")
                rows = S3Service.read_csv_file(bucket_name, csv_file)
                processed_files.append(csv_file)

                logger.info(
                    f"Starting batch upsert for file '{csv_file}' with {len(rows)} rows (batch size: {batch_size})")

                file_total = len(rows)
                file_inserted = 0
                file_updated = 0
                file_failed = 0

                for batch_start in range(0, file_total, batch_size):
                    batch = rows[batch_start:batch_start+batch_size]
                    logger.info(
                        f"Processing batch {batch_start//batch_size + 1} for file '{csv_file}': {len(batch)} rows")

                    # Process entire batch in a single transaction
                    try:
                        batch_inserted = 0
                        batch_updated = 0

                        for row in batch:
                            try:
                                # Build dict from model fields and row values
                                field_names = list(
                                    model_class.model_fields.keys())
                                # Validate data using the model class
                                validated_data = model_class.model_validate(
                                    dict(zip(field_names, row)))
                                # Check if id exists
                                obj = session.get(
                                    model_class, validated_data.id)
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
                                file_failed += 1
                                errors.append(
                                    {"file": csv_file, "row": row, "error": str(e)})

                        # Commit the entire batch
                        session.commit()
                        file_inserted += batch_inserted
                        file_updated += batch_updated
                        logger.info(
                            f"Batch {batch_start//batch_size + 1} for file '{csv_file}' committed: {batch_inserted} inserted, {batch_updated} updated")

                    except Exception as e:
                        # Rollback the entire batch if there's an error
                        session.rollback()
                        logger.error(
                            f"Batch {batch_start//batch_size + 1} for file '{csv_file}' failed and rolled back: {e}")
                        # Count all rows in this batch as failed
                        file_failed += len(batch)
                        for row in batch:
                            errors.append(
                                {"file": csv_file, "row": row, "error": f"Batch failed: {e}"})

                # Accumulate file results
                total += file_total
                inserted += file_inserted
                updated += file_updated
                failed += file_failed

                logger.info(
                    f"File '{csv_file}' completed. Inserted: {file_inserted}, Updated: {file_updated}, Failed: {file_failed}")

            except FileNotFoundError as e:
                logger.error(f"File '{csv_file}' not found: {str(e)}")
                errors.append({"file": csv_file, "file_error": str(e)})
                failed += 1
            except Exception as e:
                logger.error(f"Error processing file '{csv_file}': {str(e)}")
                errors.append({"file": csv_file, "file_error": str(e)})
                failed += 1

        logger.info(
            f"Batch upsert completed for table '{table_name}'. Processed {len(processed_files)} files. Total: {total}, Inserted: {inserted}, Updated: {updated}, Failed: {failed}")
        return {
            "table": table_name,
            "total": total,
            "inserted": inserted,
            "updated": updated,
            "failed": failed,
            "errors": errors,
            "processed_files": processed_files
        }
