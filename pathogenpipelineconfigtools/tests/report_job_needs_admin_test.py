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

  def test_has_pipeline_conf(self):
    self.assertFalse(script.is_pipeline_conf('foo'))
    self.assertFalse(script.is_pipeline_conf('foo.conf'))
    self.assertFalse(script.is_pipeline_conf('foo_pipeline'))
    self.assertTrue(script.is_pipeline_conf('foo_pipeline.conf'))
    self.assertFalse(script.is_pipeline_conf('foo_pipeline.conf.backup'))
    self.assertFalse(script.is_pipeline_conf('~/directory/foo.conf'))
    self.assertFalse(script.is_pipeline_conf('~/directory/foo_pipeline'))
    self.assertTrue(script.is_pipeline_conf('~/directory/foo_pipeline.conf'))
    self.assertFalse(script.is_pipeline_conf('~/directory/foo_pipeline.conf.backup'))
    self.assertFalse(script.is_pipeline_conf('~/directory_pipeline.conf/foo'))

  @mock.patch('pathogenpipelineconfigtools.report_job_needs_admin.get_files_in_directory')
  def test_find_job_trackers_in_folder(self, script_mock):
    script_mock.return_value = ['parent_directory/foo', 'parent_directory/foo.conf', 
                                'parent_directory/foo_pipeline', 'parent_directory/foo_pipeline.conf']
    trackers = script.find_job_trackers_in_folder('parent_directory')
    expected_trackers = ['parent_directory/foo_pipeline.conf']
    self.assertEqual(trackers, expected_trackers)

  @mock.patch('pathogenpipelineconfigtools.report_job_needs_admin.os')
  def test_just_dirs(self, os_mock):
    os_mock.path.isdir.side_effect = self.isdir

    dirs = script.just_dirs(['file_foo', 'dir_bar'])
    expected_dirs = ['dir_bar']
    self.assertEqual(dirs, expected_dirs)
  
  @mock.patch('pathogenpipelineconfigtools.report_job_needs_admin.os')
  def test_get_subdirectories(self, os_mock):
    os_mock.path.join = os.path.join
    os_mock.path.listdir.return_value = ['file_foo', 'dir_bar', 'link_baz']  
    os_mock.path.isdir.side_effect = self.isdir

    subdirs = script.get_subdirectories('parent_directory')
    self.assertEqual(subdirs, ['parent_directory/dir_bar'])

  def nested_directory(self, dirname):
    if dirname == 'dir_parent':
      return ['file_parent_pipeline.conf', 'file_parent_random', 'dir_child']
    elif dirname == 'dir_parent/dir_child':
      return ['file_child_pipeline.conf', 'file_child_random', 'dir_grandchild']
    else:
      return ['file_another_pipeline.conf', 'file_another_random', 'dir_yet_another']

  @mock.patch('pathogenpipelineconfigtools.report_job_needs_admin.os')
  def test_get_all_job_trackers(self, os_mock):
    os_mock.path.join = os.path.join
    os_mock.path.isdir.side_effect = self.isdir
    os_mock.path.isfile.side_effect = self.isfile
    os_mock.path.listdir.side_effect = self.nested_directory  
    os_mock.path.sep = '/'
    pipeline_files = script.get_all_job_trackers('dir_parent')
    expected_files = ['dir_parent/file_parent_pipeline.conf', 'dir_parent/dir_child/file_child_pipeline.conf']
    self.assertEqual(pipeline_files, expected_files)

