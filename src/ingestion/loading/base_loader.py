from abc import ABC, abstractmethod
import pandas as pd

class BaseLoader(ABC):
    def __init__(self, cfg: dict):
        self.cfg = cfg

    @abstractmethod
    def load(self) -> pd.DataFrame: ...
