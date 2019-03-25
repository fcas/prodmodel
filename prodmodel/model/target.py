from abc import abstractmethod
import hashlib
import pickle
from pathlib import Path
from os.path import abspath
import os
import logging
import json

from typing import List
from model.artifact import Artifact


class Target:
  # TODO List[Target]
  def __init__(self, sources: List[Artifact], deps: List, cache: bool):
    self.sources = sources
    self.deps = deps
    self.cache = cache
    self.cached_output = None
    self.cached_hash_id = None


  @abstractmethod
  def is_changed(self):
    pass


  @abstractmethod
  def init(self):
    pass


  @abstractmethod
  def execute(self) -> object:
    pass


  @abstractmethod
  def finish(self):
    pass


  @abstractmethod
  def params(self) -> dict:
    pass


  def init_with_deps(self):
    self.init()
    for dep in self.deps:
      dep.init_with_deps()


  def finish_with_deps(self):
    self.finish()
    for dep in self.deps:
      dep.finish_with_deps()


  def hash_id(self) -> str:
    m = hashlib.sha256()
    m.update(self.__class__.__name__.encode('utf-8'))
    m.update(json.dumps(self.params()).encode('utf-8'))
    for source in self.sources:
      m.update(source.hash_id().encode('utf-8'))
    for dep in self.deps:
      m.update(dep.hash_id().encode('utf-8'))
    return m.hexdigest()


  def output(self):
    class_name = self.__class__.__name__
    logging.info(f'Executing {class_name}.')
    hash_id = self.hash_id()
    if hash_id == self.cached_hash_id and self.cached_output is not None:
      logging.info(f'  Re-using cached version {hash_id}.')
      return self.cached_output
    else:
      root_dir = Path('target') / (class_name + '_' + hash_id)
      os.makedirs(root_dir, exist_ok=True)
      file_path = root_dir / '1.pickle'
      if file_path.is_file():
        logging.info(f'  Loading cached version {hash_id}.')
        with open(file_path, 'rb') as f:
          output = pickle.load(f)
      else:
        logging.info(f'  Creating version {hash_id}.')
        output = self.execute()
        with open(file_path, 'wb') as f:
          pickle.dump(output, f)
      self.cached_output = output
      self.cached_hash_id = hash_id
      return output
