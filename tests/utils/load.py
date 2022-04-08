import zlib
import pandas
from io import StringIO
from google.cloud import bigquery
from google.cloud import storage
from tests.utils.resources import bq_client, bucket, separator
from tests.utils.ids import build_table_id, build_bucket_uri


def wait_for_jobs(jobs):
    for job in jobs:
        job.result()


def multi_query_to_dataset(queries, table_names):
    jobs = []
    for q, n in zip(queries, table_names):
        job_config = bigquery.QueryJobConfig()
        job_config.destination = build_table_id(n)
        job_config.write_disposition = 'WRITE_TRUNCATE'
        job = bq_client.query(query=q, job_config=job_config)
        jobs.append(job)
    wait_for_jobs(jobs)


def bucket_to_local(blob_name, local_file_path):
    storage.Blob(name=blob_name, bucket=bucket).download_to_filename(
        local_file_path)


def local_to_dataframe(local_file_path):
    return pandas.read_csv(local_file_path, sep=separator)


def dataframe_to_local(dataframe, local_file_path):
    return dataframe.to_csv(local_file_path, sep=separator, index=False)


def dataset_to_dataframe(table_name):
    table_id = build_table_id(table_name)
    return bq_client.list_rows(table_id).to_dataframe()


def multi_dataframe_to_dataset(dataframes, table_names):
    jobs = []
    for df, n in zip(dataframes, table_names):
        table_id = build_table_id(n)
        job_config = bigquery.LoadJobConfig()
        job = bq_client.load_table_from_dataframe(
            dataframe=df,
            destination=table_id,
            job_config=job_config)
        jobs.append(job)
    wait_for_jobs(jobs)


def dataframe_to_bucket(dataframe, blob_name):
    csv = dataframe.to_csv(sep=separator, index=False)
    storage.Blob(name=blob_name, bucket=bucket).upload_from_string(csv)


def bucket_to_dataframe(blob_name, decompress):
    b = storage.Blob(name=blob_name, bucket=bucket).download_as_bytes()
    if decompress:
        b = zlib.decompress(b, wbits=zlib.MAX_WBITS | 16)
    csv = b.decode()
    return pandas.read_csv(StringIO(csv), sep=separator)
