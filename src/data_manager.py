import os
import pickle
import json
import pandas as pd


class DataManager:
    _data_dir: str

    def __init__(self, data_dir: str | None = None):
        if data_dir:
            self._data_dir = data_dir
        else:
            root_dir: str = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
            self._data_dir = os.path.abspath(os.path.join(root_dir, 'data'))

    def get_file_path(self, file_name: str) -> str:
        return os.path.abspath(os.path.join(self._data_dir, file_name))

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

    def dump_json(self, data: any, file_name: str) -> str:
        file_path: str = os.path.abspath(os.path.join(self._data_dir, file_name))
        with open(file_path, 'w') as f:
            json.dump(data, f)
        return file_path

    def dump_parquet(self, data: pd.DataFrame, file_name: str) -> str:
        file_path: str = os.path.abspath(os.path.join(self._data_dir, file_name))
        data.to_parquet(file_path)
        return file_path

    def load_parquet(self, file_name: str) -> pd.DataFrame:
        file_path: str = os.path.abspath(os.path.join(self._data_dir, file_name))
        return pd.read_parquet(file_path)
