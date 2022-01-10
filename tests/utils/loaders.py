from google_pandas_load import Loader, LoaderQuickSetup
from tests.utils.resources import project_id, bq_client, dataset_id, \
    dataset_name, gs_client, bucket_name, gs_dir_path, gs_subdir_path, \
    local_dir_path, local_subdir_path

gpl00 = Loader(
    bq_client=bq_client,
    dataset_id=dataset_id,
    gs_client=gs_client,
    bucket_name=bucket_name,
    gs_dir_path=None,
    local_dir_path=local_dir_path,
    separator='|',
    chunk_size=2**28)

gpl01 = Loader(
    bq_client=bq_client,
    dataset_id=dataset_id,
    gs_client=gs_client,
    bucket_name=bucket_name,
    gs_dir_path=None,
    local_dir_path=local_subdir_path,
    separator='|',
    chunk_size=2**29)

gpl10 = Loader(
    bq_client=bq_client,
    dataset_id=dataset_id,
    gs_client=gs_client,
    bucket_name=bucket_name,
    gs_dir_path=gs_dir_path,
    local_dir_path=local_dir_path,
    separator='@',
    chunk_size=2**28)

gpl11 = LoaderQuickSetup(
    project_id=project_id,
    dataset_name=dataset_name,
    bucket_name=bucket_name,
    gs_dir_path=gs_dir_path,
    local_dir_path=local_subdir_path,
    separator='|',
    chunk_size=2**28)

gpl20 = Loader(
    bq_client=bq_client,
    dataset_id=dataset_id,
    gs_client=gs_client,
    bucket_name=bucket_name,
    gs_dir_path=gs_subdir_path,
    local_dir_path=local_dir_path,
    separator='|',
    chunk_size=2**25)

gpl21 = Loader(
    bq_client=bq_client,
    dataset_id=dataset_id,
    gs_client=gs_client,
    bucket_name=bucket_name,
    gs_dir_path=gs_subdir_path,
    local_dir_path=local_subdir_path)
