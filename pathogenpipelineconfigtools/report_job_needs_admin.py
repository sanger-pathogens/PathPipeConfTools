import os
import re

def just_files(names):
  return filter(os.path.isfile, names)

def get_files_in_directory(dirname):
  contents = os.path.listdir(dirname)
  files = just_files(contents) 
  def add_path(filename):
    return os.path.join(dirname, filename)
  return map(add_path, files) 

def is_pipeline_conf(name):
  pattern = re.compile('.+_pipeline.conf$')
  match = pattern.match(name)
  return match != None

def find_job_trackers_in_folder(dirname):
  files = get_files_in_directory(dirname)
  job_trackers = filter(is_pipeline_conf, files)
  return job_trackers

def just_dirs(names):
  return filter(os.path.isdir, names)

def get_subdirectories(parent):
  contents = os.path.listdir(parent)
  dirs = just_dirs(contents)
  def add_path(child):
    return os.path.join(parent, child)
  return map(add_path, dirs)

def get_all_job_trackers(dirname):
  job_trackers = find_job_trackers_in_folder(dirname)
  child_directories = get_subdirectories(dirname)
  for child_directory in child_directories:
    job_trackers += find_job_trackers_in_folder(child_directory)
  return job_trackers 
