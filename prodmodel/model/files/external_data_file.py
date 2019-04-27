from model.files.input_file import InputFile
from model.target.external_data_target import ExternalDataTarget

from pathlib import Path


class ExternalDataFile(InputFile):

  def __init__(self, external_data_target: ExternalDataTarget):
    super().__init__(file_name=external_data_target.output_path().absolute())
    self.external_data_target = external_data_target
    self.cached_build_time = None


  def init(self, args):
    if args.force_external or not Path(self.file_name).is_file():
      # Re-create input file.
      self.external_data_target.output(force=True)
