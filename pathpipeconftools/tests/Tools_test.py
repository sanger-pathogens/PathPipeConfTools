import unittest
import mock
import os
from mock import MagicMock
from StringIO import StringIO
from pathpipeconftools.Tools import ConfigDirectory, TrackerFile, PipelineJob

class TestAdminRequired(unittest.TestCase):

  def isfile(self, name):
    name = name.split('/')[-1]
    return 'file_' in name or self.islink(name)

  def islink(self, name):
    name = name.split('/')[-1]
    return 'link_' in name

  def isdir(self, name):
    name = name.split('/')[-1]
    return 'dir_' in name

  @mock.patch('pathpipeconftools.Tools.os')
  def test_just_files(self, os_mock):
    config_dir = ConfigDirectory()
    os_mock.path.isfile.side_effect = self.isfile

    files = config_dir.just_files(['file_foo', 'dir_bar'])
    expected_files = ['file_foo']
    self.assertEqual(files, expected_files)

  @mock.patch('pathpipeconftools.Tools.os')
  def test_get_files_in_directory(self, os_mock):
    config_dir = ConfigDirectory()
    os_mock.path.join = os.path.join
    os_mock.listdir.return_value = ['file_foo', 'dir_bar', 'link_baz']
    os_mock.path.isfile.side_effect = self.isfile

    files = config_dir.get_files_in_directory('parent_directory')
    expected_files = ['parent_directory/file_foo', 'parent_directory/link_baz']

    self.assertItemsEqual(files, expected_files)
    os_mock.listdir.assert_called_with('parent_directory')

  def test_has_pipeline_conf(self):
    config_dir = ConfigDirectory()
    self.assertFalse(config_dir.is_pipeline_conf('foo'))
    self.assertFalse(config_dir.is_pipeline_conf('foo.conf'))
    self.assertFalse(config_dir.is_pipeline_conf('foo_pipeline'))
    self.assertTrue(config_dir.is_pipeline_conf('foo_pipeline.conf'))
    self.assertFalse(config_dir.is_pipeline_conf('foo_pipeline.conf.backup'))
    self.assertFalse(config_dir.is_pipeline_conf('~/directory/foo.conf'))
    self.assertFalse(config_dir.is_pipeline_conf('~/directory/foo_pipeline'))
    self.assertTrue(config_dir.is_pipeline_conf('~/directory/foo_pipeline.conf'))
    self.assertFalse(config_dir.is_pipeline_conf('~/directory/foo_pipeline.conf.backup'))
    self.assertFalse(config_dir.is_pipeline_conf('~/directory_pipeline.conf/foo'))

  def test_find_job_trackers_in_folder(self):
    config_dir = ConfigDirectory()
    script_mock = MagicMock()
    script_mock.return_value = ['parent_directory/foo', 'parent_directory/foo.conf',
                                'parent_directory/foo_pipeline', 'parent_directory/foo_pipeline.conf']
    config_dir.get_files_in_directory = script_mock
    trackers = config_dir.find_job_trackers_in_folder('parent_directory')
    expected_trackers = ['parent_directory/foo_pipeline.conf']
    self.assertEqual(trackers, expected_trackers)

  @mock.patch('pathpipeconftools.Tools.os')
  def test_just_dirs(self, os_mock):
    config_dir = ConfigDirectory()
    os_mock.path.isdir.side_effect = self.isdir

    dirs = config_dir.just_dirs(['file_foo', 'dir_bar'])
    expected_dirs = ['dir_bar']
    self.assertEqual(dirs, expected_dirs)

  @mock.patch('pathpipeconftools.Tools.os')
  def test_get_subdirectories(self, os_mock):
    config_dir = ConfigDirectory()
    os_mock.path.join = os.path.join
    os_mock.listdir.return_value = ['file_foo', 'dir_bar', 'link_baz']
    os_mock.path.isdir.side_effect = self.isdir

    subdirs = config_dir.get_subdirectories('parent_directory')
    self.assertEqual(subdirs, ['parent_directory/dir_bar'])

  def nested_directory(self, dirname):
    config_dir = ConfigDirectory()
    if dirname == 'dir_parent':
      return ['file_parent_pipeline.conf', 'file_parent_random', 'dir_child']
    elif dirname == 'dir_parent/dir_child':
      return ['file_child_pipeline.conf', 'file_child_random', 'dir_grandchild']
    else:
      return ['file_another_pipeline.conf', 'file_another_random', 'dir_yet_another']

  @mock.patch('pathpipeconftools.Tools.os')
  def test_get_all_job_tracker_filenames(self, os_mock):
    config_dir = ConfigDirectory()
    os_mock.path.join = os.path.join
    os_mock.path.isdir.side_effect = self.isdir
    os_mock.path.isfile.side_effect = self.isfile
    os_mock.listdir.side_effect = self.nested_directory
    os_mock.path.sep = '/'
    pipeline_files = config_dir.get_all_job_tracker_filenames('dir_parent')
    expected_files = ['dir_parent/file_parent_pipeline.conf', 'dir_parent/dir_child/file_child_pipeline.conf']
    self.assertEqual(pipeline_files, expected_files)

  def test_get_job_trackers(self):
    config_dir = ConfigDirectory()
    config_dir.get_all_job_tracker_filenames = MagicMock()
    pipeline_files =['dir_parent/file_parent_pipeline.conf', 'dir_parent/dir_child/file_child_pipeline.conf']
    config_dir.get_all_job_tracker_filenames.return_value = pipeline_files

    tracker_files = config_dir.get_job_trackers('dir_parent')
    self.assertEquals(len(tracker_files), 2)
    self.assertIsInstance(tracker_files[0], TrackerFile)
    self.assertIsInstance(tracker_files[1], TrackerFile)
    tracker_filenames = [tracker.path for tracker in tracker_files]
    self.assertEqual(tracker_filenames, pipeline_files)

  @mock.patch('pathpipeconftools.Tools.datetime')
  def test_to_dict(self, datetime_mock):
    datetime_mock.datetime.now.return_value.isoformat.return_value = '1900-01-01T00:00:00.000000'
    def new_job(approval_required, job_type, config_file):
      job = MagicMock()
      job.approval_required = approval_required
      job.job_type = job_type
      job.config_file = config_file
      return job

    config_dir = ConfigDirectory()
    config_dir.get_job_trackers = MagicMock()

    job_tracker = MagicMock()
    job_tracker.path = 'parent_dir/foo_pipeline.conf'
    job_tracker.get_jobs.return_value = [
      new_job(True, '__FOO__', 'parent_dir/child_dir/job_1.conf'),
      new_job(True, '__BAR__', 'parent_dir/child_dir/job_2.conf'),
      new_job(False, '__BAZ__', 'parent_dir/child_dir/job_3.conf')
    ]

    config_dir.get_job_trackers.return_value = [job_tracker]

    actual_dict = config_dir.to_dict('parent_dir')
    expected_dict = {
                      'jobs': [
                        { 'approval_required': True,
                          'job_type': '__FOO__',
                          'config_file': 'parent_dir/child_dir/job_1.conf',
                          'pipeline_tracker': 'parent_dir/foo_pipeline.conf'
                        },
                        { 'approval_required': True,
                          'job_type': '__BAR__',
                          'config_file': 'parent_dir/child_dir/job_2.conf',
                          'pipeline_tracker': 'parent_dir/foo_pipeline.conf'
                        },
                        { 'approval_required': False,
                          'job_type': '__BAZ__',
                          'config_file': 'parent_dir/child_dir/job_3.conf',
                          'pipeline_tracker': 'parent_dir/foo_pipeline.conf'
                        }
                      ],
                      'created_at': '1900-01-01T00:00:00.000000'
                    }

    self.assertEqual(actual_dict, expected_dict)



class TestJobTracker(unittest.TestCase):

  @mock.patch('pathpipeconftools.Tools.open', create=True)
  def test_get_lines(self, open_mock):
    file_like_object = StringIO('line 1\nline 2\n')
    open_mock.return_value.__enter__.return_value = file_like_object

    tracker = TrackerFile('foo')
    self.assertEquals(tracker.get_lines(), ['line 1', 'line 2'])

  def test_get_jobs(self):
    tracker = TrackerFile('foo')
    tracker.get_lines = MagicMock()
    tracker.get_lines.return_value = [
      "__VRTrack_JOB_TYPE__ /parent_dir/child_dir/job_1.conf",
      "#admin_approval_required#__VRTrack_JOB_TYPE__ /parent_dir/child_dir/job_2.conf",
      "bad config_line"
    ]

    jobs = tracker.get_jobs()
    self.assertEqual(jobs[0].job_type, '__VRTrack_JOB_TYPE__')
    self.assertEqual(jobs[0].config_file, '/parent_dir/child_dir/job_1.conf')
    self.assertEqual(jobs[0].approval_required, False)
    self.assertIsInstance(jobs[0], PipelineJob)

    self.assertEqual(jobs[1].job_type, '__VRTrack_JOB_TYPE__')
    self.assertEqual(jobs[1].config_file, '/parent_dir/child_dir/job_2.conf')
    self.assertEqual(jobs[1].approval_required, True)
    self.assertIsInstance(jobs[1], PipelineJob)

    self.assertEqual(len(jobs), 2)

class TestJob(unittest.TestCase):

  def test_init(self):
    job = PipelineJob('__VRTrack_JOB_TYPE__ /parent_dir/child_dir/job_1.conf')
    self.assertEqual(job.job_type, '__VRTrack_JOB_TYPE__')
    self.assertEqual(job.config_file, '/parent_dir/child_dir/job_1.conf')
    self.assertEqual(job.approval_required, False)

    job = PipelineJob('#admin_approval_required#__VRTrack_JOB_TYPE__ /parent_dir/child_dir/job_2.conf')
    self.assertEqual(job.job_type, '__VRTrack_JOB_TYPE__')
    self.assertEqual(job.config_file, '/parent_dir/child_dir/job_2.conf')
    self.assertEqual(job.approval_required, True)

    self.assertRaises(ValueError, PipelineJob, 'something else')
    self.assertRaises(ValueError, PipelineJob, 'other')
    self.assertRaises(ValueError, PipelineJob, '#other#__FOO__ /thing.conf')
    self.assertRaises(ValueError, PipelineJob, '#other# /thing.conf')

  def test_is_approval_required(self):
    job = PipelineJob('__FOO__ /thing.conf')
    self.assertTrue(job.is_approval_required('#admin_approval_required#__FOO__ /thing.conf'))
    self.assertTrue(job.is_approval_required('#admin_approval_required# __FOO__ /thing.conf'))
    self.assertFalse(job.is_approval_required('admin_approval_required#__FOO__ /thing.conf'))
    self.assertFalse(job.is_approval_required('__FOO__ /thing.conf'))
    self.assertFalse(job.is_approval_required('__FOO__ /thing.conf#admin_approval_required#'))

  def test_get_job_type(self):
    job = PipelineJob('__FOO__ /thing.conf')

    job_type = job.get_job_type('#admin_approval_required#__FOO__ /thing.conf')
    self.assertEqual(job_type, '__FOO__')

    job_type = job.get_job_type('#admin_approval_required# __FOO__ /thing.conf')
    self.assertEqual(job_type, '__FOO__')

    job_type = job.get_job_type('admin_approval_required#__FOO__ /thing.conf')
    self.assertEqual(job_type, None)

    job_type = job.get_job_type('__FOO__ /thing.conf')
    self.assertEqual(job_type, '__FOO__')

    job_type = job.get_job_type('__FOO__ /thing.conf#admin_approval_required#')
    self.assertEqual(job_type, '__FOO__')

    job_type = job.get_job_type('__FOO__ /thing.conf #admin_approval_required#')
    self.assertEqual(job_type, '__FOO__')

    job_type = job.get_job_type('__FOO__ /thing.conf #another comment')
    self.assertEqual(job_type, '__FOO__')

    job_type = job.get_job_type('something else')
    self.assertEqual(job_type, None)

    job_type = job.get_job_type('other')
    self.assertEqual(job_type, None)

  def test_get_job_config(self):
    job = PipelineJob('__FOO__ /thing.conf')

    job_config = job.get_job_config('#admin_approval_required#__FOO__ /thing.conf')
    self.assertEqual(job_config, '/thing.conf')

    job_config = job.get_job_config('#admin_approval_required# __FOO__ /thing.conf')
    self.assertEqual(job_config, '/thing.conf')

    job_config = job.get_job_config('admin_approval_required#__FOO__ /thing.conf')
    self.assertEqual(job_config, None)

    job_config = job.get_job_config('__FOO__ /thing.conf')
    self.assertEqual(job_config, '/thing.conf')

    job_config = job.get_job_config('__FOO__ /thing.conf ')
    self.assertEqual(job_config, '/thing.conf')

    job_config = job.get_job_config('__FOO__ /thing.conf#admin_approval_required#')
    self.assertEqual(job_config, '/thing.conf')

    job_config = job.get_job_config('__FOO__ /thing.conf #admin_approval_required#')
    self.assertEqual(job_config, '/thing.conf')

    job_config = job.get_job_config('__FOO__ /thing.conf #another comment')
    self.assertEqual(job_config, '/thing.conf')

    job_type = job.get_job_type('something else')
    self.assertEqual(job_type, None)

    job_type = job.get_job_type('other')
    self.assertEqual(job_type, None)
