import os
from tests.context.loaders import gpl1, gpl2, gpl3
from tests.context.resources import bucket_name, local_dir_path
from tests.base_class import BaseClassTest
from tests.populate import populate_bucket, populate_local_folder


class ListMethodsTest(BaseClassTest):

    def test_list_blobs(self):
        populate_bucket()

        self.assertEqual(
            sorted([b.name for b in gpl1.list_blobs('a')]),
            sorted([f'a{i}_gs' for i in range(9, 12)]))

        self.assertEqual(
            sorted([b.name for b in gpl1.list_blobs('a1')]),
            sorted([f'a{i}_gs' for i in range(10, 12)]))

        self.assertEqual(
            sorted([b.name for b in gpl2.list_blobs('a')]),
            sorted([f'dir/subdir/a{i}_gs' for i in range(7, 11)]))

        self.assertEqual(
            sorted([b.name for b in gpl2.list_blobs('a1')]),
            sorted([f'dir/subdir/a{i}_gs' for i in range(10, 11)]))

    def test_list_blob_uris(self):
        populate_bucket()

        self.assertEqual(
            sorted(gpl1.list_blob_uris('a')),
            sorted([f'gs://{bucket_name}/a{i}_gs' for i in range(9, 12)]))

        self.assertEqual(
            sorted(gpl1.list_blob_uris('a1')),
            sorted([f'gs://{bucket_name}/a{i}_gs' for i in range(10, 12)]))

        self.assertEqual(
            sorted(gpl2.list_blob_uris('a')),
            sorted([f'gs://{bucket_name}/dir/subdir/a{i}_gs'
                    for i in range(7, 11)]))

        self.assertEqual(
            sorted(gpl2.list_blob_uris('a1')),
            sorted([f'gs://{bucket_name}/dir/subdir/a{i}_gs'
                    for i in range(10, 11)]))

    def test_list_local_file_paths(self):
        populate_local_folder()

        self.assertEqual(
            sorted([os.path.normpath(p) for p
                    in gpl3.list_local_file_paths('a')]),
            sorted([os.path.normpath(
                os.path.join(local_dir_path, f'a{i}_local'))
                for i in range(9, 14)]))

        self.assertEqual(
            sorted([os.path.normpath(p) for p
                    in gpl3.list_local_file_paths('a1')]),
            sorted([os.path.normpath(
                os.path.join(local_dir_path, f'a{i}_local'))
                for i in range(10, 14)]))
