"""
Attention-based model for time series
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class AttentionMechanism(nn.Module):
    """Self-attention mechanism"""
    
    def __init__(self, hidden_size: int):
        super().__init__()
        self.hidden_size = hidden_size
        
        self.query = nn.Linear(hidden_size, hidden_size)
        self.key = nn.Linear(hidden_size, hidden_size)
        self.value = nn.Linear(hidden_size, hidden_size)
        self.scale = torch.sqrt(torch.FloatTensor([hidden_size]))
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass with attention"""
        Q = self.query(x)
        K = self.key(x)
        V = self.value(x)
        
        # Attention scores
        attention = torch.matmul(Q, K.transpose(-2, -1)) / self.scale.to(x.device)
        attention = F.softmax(attention, dim=-1)
        
        # Apply attention to values
        out = torch.matmul(attention, V)
        
        return out, attention


class AttentionLSTM(nn.Module):
    """LSTM with attention"""
    
    def __init__(
        self,
        input_size: int,
        hidden_size: int = 128,
        num_layers: int = 2,
        output_size: int = 1,
    ):
        super().__init__()
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
        )
        
        self.attention = AttentionMechanism(hidden_size * 2)  # *2 for bidirectional
        self.fc = nn.Linear(hidden_size * 2, output_size)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        # LSTM
        lstm_out, _ = self.lstm(x)  # [batch, seq, hidden*2]
        
        # Attention
        attn_out, _ = self.attention(lstm_out)
        
        # Global average pooling
        out = torch.mean(attn_out, dim=1)
        
        # Final prediction
        out = self.fc(out)
        
        return out
