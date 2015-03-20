import os
import re

class ConfigDirectory(object):
  def just_files(self, names):
    return filter(os.path.isfile, names)

  def get_files_in_directory(self, dirname):
    contents = os.path.listdir(dirname)
    files = self.just_files(contents)
    def add_path(filename):
      return os.path.join(dirname, filename)
    return map(add_path, files)

  def is_pipeline_conf(self, name):
    pattern = re.compile('.+_pipeline.conf$')
    match = pattern.match(name)
    return match != None

  def find_job_trackers_in_folder(self, dirname):
    files = self.get_files_in_directory(dirname)
    job_trackers = filter(self.is_pipeline_conf, files)
    return job_trackers

  def just_dirs(self, names):
    return filter(os.path.isdir, names)

  def get_subdirectories(self, parent):
    contents = os.path.listdir(parent)
    dirs = self.just_dirs(contents)
    def add_path(child):
      return os.path.join(parent, child)
    return map(add_path, dirs)

  def get_all_job_tracker_filenames(self, dirname):
    job_trackers = self.find_job_trackers_in_folder(dirname)
    child_directories = self.get_subdirectories(dirname)
    for child_directory in child_directories:
      job_trackers += self.find_job_trackers_in_folder(child_directory)
    return job_trackers

  def get_job_trackers(self, dirname):
    job_tracker_filenames = self.get_all_job_tracker_filenames(dirname)
    return [TrackerFile(filename) for filename in job_tracker_filenames]

class TrackerFile(object):
  def __init__(self, path):
    self.path = path
