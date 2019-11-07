import uuid
from argparse import Namespace
import numpy
from google.cloud import bigquery
from google_pandas_load.utils import build_atomic_function_names, \
    build_numpy_leaf_types
from google_pandas_load.constants import LOCATIONS, REVERSED_LOCATIONS, \
    MIDDLE_LOCATIONS

integer_numpy_leaf_types = build_numpy_leaf_types(dtype=numpy.integer)
float_numpy_leaf_types = build_numpy_leaf_types(dtype=numpy.floating)


class LoadConfig:
    """Configuration for a load job.

    This class has the same parameters as
    :meth:`google_pandas_load.loader.Loader.load`. It is used to launch
    simultaneously load jobs as follows:

    - A list of LoadConfig is built.
    - The list is passed to :meth:`google_pandas_load.loader.Loader.mload`.
    """

    def __init__(
            self,
            source,
            destination,

            data_name=None,
            query=None,
            dataframe=None,

            overwrite=False,
            dtype=None,
            parse_dates=None,
            infer_datetime_format=True,
            date_cols=None,
            timestamp_cols=None,
            bq_schema=None):

        self._source = source
        self._destination = destination

        self.data_name = data_name
        self._query = query
        self._dataframe = dataframe

        self._overwrite = overwrite
        self._dtype = dtype
        self._parse_dates = parse_dates
        self._infer_datetime_format = infer_datetime_format
        self._timestamp_cols = timestamp_cols
        self._date_cols = date_cols
        self._bq_schema = bq_schema

        self._check_source_destination()
        self._check_required_arguments()

        self._transitional_data_name = (
            self.data_name + '_' + str(uuid.uuid1().int))

        if self._bq_schema is None and self._dataframe is not None:
            self._infer_bq_schema_from_dataframe()

    def _check_source_value(self):
        msg = """
        source must be one of 'query' or 'bq' or 'gs' or 'local' or 'dataframe
        """
        if self._source not in LOCATIONS:
            raise ValueError(msg)

    def _check_destination_value(self):
        msg = """
        destination must be one of 'query' or 'bq' or 'gs' or'local' or 
        'dataframe'
        """
        if self._destination not in LOCATIONS:
            raise ValueError(msg)

    def _check_source_different_from_destination(self):
        if self._source == self._destination:
            raise ValueError('source must be different from destination')

    def _check_if_query_missing(self):
        if self._source == 'query' and self._query is None:
            raise ValueError("query must be given if source = 'query'")

    def _check_if_dataframe_missing(self):
        if self._source == 'dataframe' and self._dataframe is None:
            raise ValueError("dataframe must be given if source = 'dataframe'")

    def _check_if_data_name_missing(self):
        msg = """
        data_name must be given if source or destination is one of 'bq' or 'gs' 
        or 'local'
        """
        condition_1 = self.data_name is None
        condition_2 = self._source in MIDDLE_LOCATIONS
        condition_3 = self._destination in MIDDLE_LOCATIONS

        if condition_1 and (condition_2 or condition_3):
            raise ValueError(msg)

    def _check_if_bq_schema_missing(self):
        condition_1 = self._source in ('local', 'gs')
        condition_2 = self._destination in ('bq', 'query')
        condition_3 = self._bq_schema is None
        if condition_1 and condition_2 and condition_3:
            raise ValueError('bq_schema is missing')

    @property
    def _names_of_atomic_functions_to_call(self):
        index_source = LOCATIONS.index(self._source)
        index_destination = LOCATIONS.index(self._destination)
        rindex_source = REVERSED_LOCATIONS.index(self._source)
        rindex_destination = REVERSED_LOCATIONS.index(self._destination)
        if index_source < index_destination:
            return build_atomic_function_names(
                LOCATIONS[index_source: index_destination + 1])
        else:
            return build_atomic_function_names(
                REVERSED_LOCATIONS[rindex_source: rindex_destination + 1])

    @property
    def _number_of_atomic_functions_to_call(self):
        return len(self._names_of_atomic_functions_to_call)

    @staticmethod
    def bq_schema_inferred_from_dataframe(
            dataframe, date_cols=None, timestamp_cols=None):
        """Return a BigQuery schema that is inferred from a pandas dataframe.

        In BigQuery, a column is given its type according to the following
        rule:

        - if its name is listed in the date_cols parameter, its type in
          BigQuery should be DATE.
        - elif  its name is listed in the timestamp_cols parameter, its type
          in BigQuery should be TIMESTAMP.
        - elif its pandas dtype is equal to numpy.bool, its type in BigQuery
          is BOOLEAN.
        - elif its pandas dtype has numpy.integer dtype as ancestor, its type
          in BigQuery is INTEGER.
        - elif its pandas dtype has numpy.floating dtype as ancestor, its type
          in BigQuery is FLOAT.
        - else its type in BigQuery is STRING.

        Args:
            dataframe (pandas.DataFrame): The dataframe.
            date_cols (list of str, optional): The names of the columns
                receiving the BigQuery type DATE.
            timestamp_cols (list of str, optional): The names of the columns
                receiving the BigQuery type TIMESTAMP.

        Returns:
            list of google.cloud.bigquery.schema.SchemaField: A BigQuery
            schema.
        """
        if len(dataframe.columns) == 0:
            raise ValueError(
                'A non empty bq_schema cannot be inferred '
                'from a dataframe with no columns')
        if timestamp_cols is None:
            timestamp_cols = []
        if date_cols is None:
            date_cols = []
        bq_schema = []
        for col in dataframe.columns:
            dtype = dataframe[col].dtype
            if col in date_cols:
                bq_schema.append(bigquery.SchemaField(name=col,
                                                      field_type='DATE'))
            elif col in timestamp_cols:
                bq_schema.append(bigquery.SchemaField(name=col,
                                                      field_type='TIMESTAMP'))
            elif dtype == numpy.bool:
                bq_schema.append(bigquery.SchemaField(name=col,
                                                      field_type='BOOLEAN'))
            elif dtype in integer_numpy_leaf_types:
                bq_schema.append(bigquery.SchemaField(name=col,
                                                      field_type='INTEGER'))
            elif dtype in float_numpy_leaf_types:
                bq_schema.append(bigquery.SchemaField(name=col,
                                                      field_type='FLOAT'))
            else:
                bq_schema.append(bigquery.SchemaField(name=col,
                                                      field_type='STRING'))
        return bq_schema

    def _infer_bq_schema_from_dataframe(self):
        self._bq_schema = self.bq_schema_inferred_from_dataframe(
            dataframe=self._dataframe,
            timestamp_cols=self._timestamp_cols,
            date_cols=self._date_cols)

    def _source_data_name(self, atomic_function_position):
        if atomic_function_position == 0:
            return self.data_name
        else:
            return self._transitional_data_name

    def _destination_data_name(self, atomic_function_position):
        if atomic_function_position == (
                self._number_of_atomic_functions_to_call - 1):
            return self.data_name
        else:
            return self._transitional_data_name

    def _is_last_atomic_function(self, atomic_function_position):
        return atomic_function_position == (
                self._number_of_atomic_functions_to_call - 1)

    @staticmethod
    def _delete_in_source(atomic_function_position):
        return atomic_function_position != 0

    def _query_to_bq_config(self, position):
        return Namespace(
            is_destination_transitional=self._is_last_atomic_function(position),
            destination_data_name=self._destination_data_name(position),
            query=self._query,
            write_disposition=self._write_disposition)

    def _bq_to_gs_config(self, position):
        return Namespace(
            source_data_name=self._source_data_name(position),
            destination_data_name=self._destination_data_name(position),
            delete_in_source=self._delete_in_source(position))

    def _gs_to_local_config(self, position):
        return Namespace(
            source_data_name=self._source_data_name(position),
            destination_data_name=self._destination_data_name(position),
            delete_in_source=self._delete_in_source(position))

    def _local_to_dataframe_config(self, position):
        return Namespace(
            source_data_name=self._source_data_name(position),
            destination_data_name=self._destination_data_name(position),
            delete_in_source=self._delete_in_source(position),
            dtype=self._dtype,
            parse_dates=self._parse_dates,
            infer_datetime_format=self._infer_datetime_format)

    def _dataframe_to_local_config(self, position):
        return Namespace(
            source_data_name=self._source_data_name(position),
            dataframe=self._dataframe)

    def _local_to_gs(self, position):
        return Namespace(
            source_data_name=self._source_data_name(position),
            destination_data_name=self._destination_data_name(position),
            delete_in_source=self._delete_in_source(position))

    def _gs_to_bq_config(self, position):
        return Namespace(
            source_data_name=self._source_data_name(position),
            destination_data_name=self._destination_data_name(position),
            delete_in_source=self._delete_in_source(position),
            schema=self._bq_schema,
            write_disposition=self._write_disposition)

    def _bq_to_query_config(self, position):
        return Namespace(
            source_data_name=self._source_data_name(position))

    @property
    def atomic_configs(self):
        res = dict()
        for i, n in enumerate(self._names_of_atomic_functions_to_call):
            res[n] = self.__dict__[n + '_config'](i)
        return res
