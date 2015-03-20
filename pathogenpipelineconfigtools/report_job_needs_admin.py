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
