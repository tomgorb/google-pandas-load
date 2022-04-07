from google.cloud import bigquery
from google.cloud import storage


project_id = 'dmp-y-tests'
dataset_name = 'test_gpl'
dataset_id = f'{project_id}.{dataset_name}'
bucket_name = 'bucket_gpl'
bucket_dir_path = 'dir'
bucket_subdir_path = bucket_dir_path + '/subdir'
local_dir_path = '/tmp/dir_gpl'
local_subdir_path = local_dir_path + '/subdir'
separator = '|'
bq_client = bigquery.Client(project=project_id)
gs_client = storage.Client(project=project_id)
bucket = gs_client.bucket(bucket_name)
