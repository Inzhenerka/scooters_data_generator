import os
import pickle
import pandas as pd


class DataManager:
    _data_dir: str

    def __init__(self, data_dir: str | None = None):
        if data_dir:
            self._data_dir = data_dir
        else:
            root_dir: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
            self._data_dir = os.path.abspath(os.path.join(root_dir, 'data'))

    def dump_pickle(self, data: any, file_name: str) -> str:
        file_path: str = os.path.abspath(os.path.join(self._data_dir, file_name))
        if not os.path.exists(self._data_dir):
            os.makedirs(self._data_dir)
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
        return file_path

    def load_pickle(self, file_name: str) -> any:
        file_path: str = os.path.abspath(os.path.join(self._data_dir, file_name))
        with open(file_path, 'rb') as f:
            return pickle.load(f)

    def load_csv(self, file_name: str) -> pd.DataFrame:
        file_path: str = os.path.abspath(os.path.join(self._data_dir, file_name))
        df: pd.DataFrame = pd.read_csv(file_path)
        return df
