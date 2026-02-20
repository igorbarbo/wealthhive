"""
LSTM model for time series prediction
"""

from typing import Any, Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset


class LSTMModel(nn.Module):
    """LSTM neural network"""
    
    def __init__(
        self,
        input_size: int,
        hidden_size: int = 128,
        num_layers: int = 2,
        output_size: int = 1,
        dropout: float = 0.2,
    ):
        super().__init__()
        
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
        )
        
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(hidden_size, output_size)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        # Initialize hidden state
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).to(x.device)
        
        # LSTM layer
        out, _ = self.lstm(x, (h0, c0))
        
        # Take last time step
        out = out[:, -1, :]
        
        # Dropout and fully connected
        out = self.dropout(out)
        out = self.fc(out)
        
        return out


class TimeSeriesDataset(Dataset):
    """Dataset for time series"""
    
    def __init__(self, X: np.ndarray, y: np.ndarray, seq_length: int):
        self.X = X
        self.y = y
        self.seq_length = seq_length
    
    def __len__(self):
        return len(self.X) - self.seq_length
    
    def __getitem__(self, idx):
        return (
            torch.FloatTensor(self.X[idx:idx + self.seq_length]),
            torch.FloatTensor([self.y[idx + self.seq_length]]),
        )


class LSTMPredictor:
    """LSTM predictor wrapper"""
    
    def __init__(
        self,
        input_size: int,
        hidden_size: int = 128,
        num_layers: int = 2,
        seq_length: int = 60,
        device: str = None,
    ):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.seq_length = seq_length
        
        self.model = LSTMModel(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
        ).to(self.device)
        
        self.criterion = nn.MSELoss()
        self.optimizer = None
    
    def prepare_data(
        self,
        X: np.ndarray,
        y: np.ndarray,
        batch_size: int = 32,
    ) -> DataLoader:
        """Prepare data loader"""
        dataset = TimeSeriesDataset(X, y, self.seq_length)
        return DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    def train(
        self,
        train_loader: DataLoader,
        epochs: int = 100,
        learning_rate: float = 0.001,
    ) -> List[float]:
        """Train model"""
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        
        losses = []
        self.model.train()
        
        for epoch in range(epochs):
            epoch_loss = 0
            for batch_X, batch_y in train_loader:
                batch_X = batch_X.to(self.device)
                batch_y = batch_y.to(self.device)
                
                self.optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = self.criterion(outputs, batch_y)
                
                loss.backward()
                self.optimizer.step()
                
                epoch_loss += loss.item()
            
            avg_loss = epoch_loss / len(train_loader)
            losses.append(avg_loss)
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch [{epoch+1}/{epochs}], Loss: {avg_loss:.6f}")
        
        return losses
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions"""
        self.model.eval()
        
        predictions = []
        with torch.no_grad():
            for i in range(len(X) - self.seq_length):
                seq = torch.FloatTensor(X[i:i + self.seq_length]).unsqueeze(0).to(self.device)
                pred = self.model(seq).cpu().numpy()
                predictions.append(pred[0][0])
        
        return np.array(predictions)
    
    def save(self, path: str):
        """Save model"""
        torch.save({
            "model_state_dict": self.model.state_dict(),
            "seq_length": self.seq_length,
        }, path)
    
    def load(self, path: str):
        """Load model"""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.seq_length = checkpoint.get("seq_length", self.seq_length)
