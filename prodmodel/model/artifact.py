from datetime import datetime
import os
import hashlib


BLOCKSIZE = 65536
    

class Artifact:

  def __init__(self, file_name: str):
    self.file_name = file_name
    self.last_modified = None
    self.cached_hash_id = None


  def hash_id(self):
    last_modified = os.path.getmtime(self.file_name)
    if self.cached_hash_id:
      if self.last_modified == last_modified:
        return self.cached_hash_id
    m = hashlib.md5()
    with open(self.file_name, 'rb') as f:
      buf = f.read(BLOCKSIZE)
      while len(buf) > 0:
        m.update(buf)
        buf = f.read(BLOCKSIZE)
    self.cached_hash_id = m.hexdigest()
    self.last_modified = last_modified
    return self.cached_hash_id
