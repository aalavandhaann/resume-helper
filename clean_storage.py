import pathlib
import shutil

BASE_PATH: pathlib.Path = pathlib.Path(__file__).parent
FILES_DIRECTORY: pathlib.Path = BASE_PATH.joinpath('files')

shutil.rmtree(f'{FILES_DIRECTORY}')