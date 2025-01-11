import boto3
import pymysql
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

# AWS S3, RDS, and Glue clients
s3 = boto3.client('s3')
glue = boto3.client('glue')
rds_endpoint = 'your-rds-endpoint'
rds_db = 'your-db-name'
rds_user = 'your-db-user'
rds_password = 'your-db-password'

def read_from_s3(bucket_name, file_key):
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        data = response['Body'].read().decode('utf-8')
        return data
    except NoCredentialsError:
        print("Credentials not available for S3.")
    except PartialCredentialsError:
        print("Incomplete credentials provided for S3.")
    except Exception as e:
        print(f"Error reading from S3: {e}")
    return None

def push_to_rds(data):
    try:
        connection = pymysql.connect(host=rds_endpoint,
                                      user=rds_user,
                                      password=rds_password,
                                      database=rds_db)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO your_table (column_name) VALUES (%s)", (data,))
        connection.commit()
    except pymysql.MySQLError as e:
        print(f"RDS Error: {e}")
        return False
    except Exception as e:
        print(f"Error with RDS operation: {e}")
        return False
    finally:
        if connection:
            connection.close()
    return True

def push_to_glue(data):
    try:
        # Example of putting data to an S3 location for Glue to read
        s3_output_bucket = 'your-glue-s3-bucket'
        s3_output_key = 'your-output-data-folder/data.csv'
        s3.put_object(Bucket=s3_output_bucket, Key=s3_output_key, Body=data)

        # Optionally, you can trigger a Glue job here to process the data.
        # Example of triggering a Glue job (this assumes you have already set up a Glue job):
        # glue_job_name = 'your-glue-job'
        # glue.start_job_run(JobName=glue_job_name)

        print(f"Data pushed to Glue via S3: s3://{s3_output_bucket}/{s3_output_key}")
    except Exception as e:
        print(f"Glue Error: {e}")

def main():
    bucket_name = 'your-bucket-name'
    file_key = 'your-file-key'
    
    # Read data from S3
    data = read_from_s3(bucket_name, file_key)
    if not data:
        print("No data found in S3.")
        return

    # Try pushing data to RDS
    if not push_to_rds(data):
        print("Failed to push data to RDS. Attempting to push to Glue...")
        push_to_glue(data)

if __name__ == "__main__":
    main()