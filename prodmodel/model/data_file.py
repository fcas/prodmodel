import importlib
import csv

from model.artifact import Artifact


class DataFile(Artifact):

  def __init__(self, file_name: str):
    super().__init__(file_name=file_name)


  def init(self):
    self.original_hash_id = self.hash_id()


  def __iter__(self):
    f = open(self.file_name, newline='')
    return csv.DictReader(f, delimiter=',')