# Mock surprise library for testing Streamlit app
import numpy as np
import pandas as pd

class Reader:
    def __init__(self, rating_scale=(0.5, 5)):
        self.rating_scale = rating_scale

class Dataset:
    def __init__(self, df):
        self.df = df
    
    @classmethod
    def load_from_df(cls, df, reader):
        return cls(df)
    
    def build_full_trainset(self):
        return MockTrainset(self.df)

class MockTrainset:
    def __init__(self, df):
        self.df = df

class SVD:
    def __init__(self, random_state=42, n_factors=50, n_epochs=50, lr_all=0.005, reg_all=0.1):
        self.random_state = random_state
        self.n_factors = n_factors
        self.fitted = False
    
    def fit(self, trainset):
        self.fitted = True
        return self
    
    def predict(self, uid, iid, verbose=False):
        # Return a mock prediction
        return MockPrediction(uid, iid, np.random.uniform(1, 5))

class SVDpp:
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.fitted = False
    
    def fit(self, trainset):
        self.fitted = True
        return self
    
    def predict(self, uid, iid, verbose=False):
        return MockPrediction(uid, iid, np.random.uniform(1, 5))

class MockPrediction:
    def __init__(self, uid, iid, est):
        self.uid = uid
        self.iid = iid
        self.est = est  # estimated rating