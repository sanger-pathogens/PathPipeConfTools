import unittest
import mock
import os
from pathogenpipelineconfigtools import report_job_needs_admin as script

class TestAdminRequired(unittest.TestCase):

  def isfile(self, name):
    return 'file' in name or self.islink(name)

  def islink(self, name):
    return 'link' in name

  def isdir(self, name):
    return 'dir' in name

  @mock.patch('pathogenpipelineconfigtools.report_job_needs_admin.os')
  def test_just_files(self, os_mock):
    os_mock.path.isfile.side_effect = self.isfile

    files = script.just_files(['file_foo', 'dir_bar'])
    expected_files = ['file_foo']
    self.assertEqual(files, expected_files)
  
  @mock.patch('pathogenpipelineconfigtools.report_job_needs_admin.os')
  def test_get_files_in_directory(self, os_mock):
    os_mock.path.join = os.path.join
    os_mock.path.listdir.return_value = ['file_foo', 'dir_bar', 'link_baz']  
    os_mock.path.isfile.side_effect = self.isfile

    files = script.get_files_in_directory('parent_directory')
    expected_files = ['parent_directory/file_foo', 'parent_directory/link_baz']

    self.assertItemsEqual(files, expected_files)
    os_mock.path.listdir.assert_called_with('parent_directory')

