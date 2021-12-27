from google.cloud import bigquery, storage
from google_pandas_load.loader import Loader


class LoaderQuickSetup(Loader):
    """
    The purpose of this class is to quickly set up a loader.

    An instance of LoaderQuickSetup is simply an instance of the base class
    built with the following arguments:

    ::

         bq_client=bq_client
         dataset_id=dataset_id
         bucket=bucket
         gs_dir_path=gs_dir_path
         local_dir_path=local_dir_path
         separator=separator
         chunk_size=chunk_size
         logger=logger

    where

    ::

        bq_client = google.cloud.bigquery.Client(
            project=project_id,
            credentials=credentials)
        dataset_id = project_id + '.' + dataset_name
        gs_client = google.cloud.storage.Client(
            project=project_id,
            credentials=credentials)
        bucket = google.cloud.storage.Bucket(
            client=gs_client,
            name=bucket_name)

    Args:
        project_id (str, optional): The project id.
        dataset_name (str, optional): The dataset name.
        bucket_name (str, optional): The bucket name.
        gs_dir_path (str, optional): See base class.
        credentials (google.auth.credentials.Credentials): Credentials used to
            build the bq_client and the bucket. If not passed, falls back to
            the default inferred from the environment.
        local_dir_path (str, optional): See base class.
        separator (str, optional): See base class.
        chunk_size (int, optional): See base class.
    """

    def __init__(
            self,
            project_id=None,
            dataset_name=None,
            bucket_name=None,
            gs_dir_path=None,
            credentials=None,
            local_dir_path=None,
            separator='|',
            chunk_size=2 ** 28):
        self._project_id = project_id
        bq_client = None
        dataset_id = None
        self._gs_client = None
        bucket = None
        if self._project_id is not None:
            bq_client = bigquery.Client(
                project=self._project_id, credentials=credentials)
            if dataset_name is not None:
                dataset_id = f'{self._project_id}.{dataset_name}'
            if bucket_name is not None:
                self._gs_client = storage.Client(
                    project=self._project_id, credentials=credentials)
                bucket = storage.Bucket(
                    client=self._gs_client, name=bucket_name)

        super().__init__(
            bq_client=bq_client,
            dataset_id=dataset_id,
            bucket=bucket,
            gs_dir_path=gs_dir_path,
            local_dir_path=local_dir_path,
            separator=separator,
            chunk_size=chunk_size)

    @property
    def project_id(self):
        """str: The project_id given in the argument."""
        return self._project_id

    @property
    def gs_client(self):
        """google.cloud.storage.client.Client: The Storage client used to
        create the bucket."""
        return self._gs_client
