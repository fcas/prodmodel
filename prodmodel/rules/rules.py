from typing import Tuple, List, Dict
from pathlib import Path
import pip._internal
import sys
import os
import hashlib

from model.files.data_file import DataFile
from model.files.external_data_file import ExternalDataFile
from model.target.target import Target
from model.target.data_target import DataTarget
from model.target.iterable_data_target import IterableDataTarget
from model.target.csv_data_target import CSVDataTarget
from model.target.transform_data_target import TransformDataTarget
from model.target.transform_stream_data_target import TransformStreamDataTarget
from model.target.select_data_target import SelectDataTarget
from model.target.sample_data_target import SampleDataTarget
from model.target.label_encoder_target import LabelEncoderTarget
from model.target.encode_label_data_target import EncodeLabelDataTarget
from model.target.test_target import TestTarget
from model.target.external_data_target import ExternalDataTarget
from model.target.pickle_data_target import PickleDataTarget
from model.file_cache import PyFileCache
from util import RuleException, checkargtypes
from globals import TargetConfig


def requirements(packages: List[str]):
  m = hashlib.sha256()
  for package in packages:
    m.update(package.encode('utf-8'))
  hash_id = m.hexdigest()
  lib_dir = str((TargetConfig.target_base_dir / 'lib' / hash_id).resolve())
  if not os.path.isdir(lib_dir):
    return_value = pip._internal.main(['install', f'--target={lib_dir}', '--ignore-installed'] + packages)
    if return_value > 0:
      raise RuleException('Error happened while installing requirements.')
  sys.path.insert(0, lib_dir)


@checkargtypes
def data_source(file: str, type: str, dtypes: dict, cache: bool=False) -> IterableDataTarget:
  assert type == 'csv'
  return CSVDataTarget(DataFile(file), dtypes, cache)


@checkargtypes
def split(data: IterableDataTarget, test_ratio: float, target_column: str, seed:int=0) -> Tuple[IterableDataTarget, IterableDataTarget, IterableDataTarget, IterableDataTarget]:
  train_data = SampleDataTarget(data, 1.0 - test_ratio, seed)
  test_data = SampleDataTarget(data, test_ratio, seed)
  train_x = SelectDataTarget(train_data, [target_column], keep=False)
  train_y = SelectDataTarget(train_data, [target_column], keep=True)
  test_x  = SelectDataTarget(test_data,  [target_column], keep=False)
  test_y  = SelectDataTarget(test_data,  [target_column], keep=True)
  return train_x, train_y, test_x, test_y


@checkargtypes
def transform_stream(file: str, fn: str, stream: IterableDataTarget, objects: Dict[str, DataTarget]={}, file_deps: List[str]=[], cache: bool=False) -> IterableDataTarget:
  return TransformStreamDataTarget(
    source=PyFileCache.get(file),
    fn=fn,
    stream=stream,
    objects=objects,
    file_deps=[PyFileCache.get(f) for f in file_deps],
    cache=cache)


@checkargtypes
def transform(file: str, fn: str, streams: Dict[str, IterableDataTarget]={}, objects: Dict[str, DataTarget]={}, file_deps: List[str]=[], cache: bool=False) -> DataTarget:
  return TransformDataTarget(
    source=PyFileCache.get(file),
    fn=fn,
    streams=streams,
    objects=objects,
    file_deps=[PyFileCache.get(f) for f in file_deps],
    cache=cache)


@checkargtypes
def create_label_encoder(data: IterableDataTarget, columns: List[str]) -> LabelEncoderTarget:
  return LabelEncoderTarget(data, columns)


@checkargtypes
def encode_labels(data: IterableDataTarget, label_encoder: LabelEncoderTarget) -> IterableDataTarget:
  return EncodeLabelDataTarget(data, label_encoder)


@checkargtypes
def test(test_file: str, file_deps: List[str], cache: bool=False):
  return TestTarget(
    test_file=PyFileCache.get(test_file),
    file_deps=[PyFileCache.get(f) for f in file_deps],
    cache=cache)


@checkargtypes
def external_data(file: str, fn: str, args: Dict[str, str]) -> ExternalDataTarget:
  external_data_target = ExternalDataTarget(source=PyFileCache.get(file), fn=fn, args=args)
  return PickleDataTarget(ExternalDataFile(external_data_target))
