import csv

from model.files.data_file import DataFile
from model.target.iterable_data_target import IterableDataTarget


class CSVDataTarget(IterableDataTarget):
  def __init__(self, source: DataFile, dtypes: dict, cache: bool):
    super().__init__(sources=[source], deps=[], file_deps=[], cache=cache)
    self.source = source
    self.dtypes = dtypes


  def __iter__(self):
    def convert(record):
      for feature_name, feature_type in self.dtypes.items():
        record[feature_name] = feature_type(record[feature_name])
      return record
    return map(convert, self.source.__iter__())


  def params(self) -> dict:
    return {'dtypes': {k: str(v) for k, v in self.dtypes.items()}}
