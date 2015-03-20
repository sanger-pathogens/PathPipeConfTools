import os

def just_files(names):
  return filter(os.path.isfile, names)

def get_files_in_directory(dirname):
  contents = os.path.listdir(dirname)
  files = just_files(contents) 
  def add_path(filename):
    return os.path.join(dirname, filename)
  return map(add_path, files) 
