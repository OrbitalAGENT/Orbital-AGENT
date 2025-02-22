# src/analytics/anomaly_detector.py
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List

class AnomalyDetector:
    def __init__(self, contamination: float = 0.01):
        self.model = IsolationForest(contamination=contamination)
        self.trained = False
        
    def train(self, data: List[List[float]]) -> None:
        X = np.array(data)
        self.model.fit(X)
        self.trained = True
        
    def detect(self, data_point: List[float]) -> bool:
        if not self.trained:
            raise RuntimeError("Model not trained")
        return self.model.predict([data_point])[0] == -1
    
    def batch_detect(self, data_points: List[List[float]]) -> List[bool]:
        if not self.trained:
            raise RuntimeError("Model not trained")
        predictions = self.model.predict(data_points)
        return [pred == -1 for pred in predictions]
