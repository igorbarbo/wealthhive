"""
Drawdown analysis
"""

from typing import Dict, List

import numpy as np
import pandas as pd


class DrawdownAnalyzer:
    """
    Analyze portfolio drawdowns
    """
    
    def analyze(self, equity_curve: pd.Series) -> Dict:
        """
        Analyze drawdowns in equity curve
        
        Returns:
            Dict with drawdown statistics
        """
        # Calculate running maximum
        running_max = equity_curve.expanding().max()
        
        # Calculate drawdown
        drawdown = (equity_curve - running_max) / running_max
        
        # Find drawdown periods
        is_drawdown = drawdown < 0
        drawdown_starts = is_drawdown & (~is_drawdown.shift(1).fillna(False))
        drawdown_ends = (~is_drawdown) & is_drawdown.shift(1).fillna(False)
        
        # Calculate statistics
        max_drawdown = drawdown.min()
        max_dd_date = drawdown.idxmin()
        
        # Find recovery
        peak_before_dd = running_max.loc[:max_dd_date].iloc[-1]
        recovery_dates = equity_curve.loc[max_dd_date:][equity_curve >= peak_before_dd]
        
        if len(recovery_dates) > 0:
            recovery_date = recovery_dates.index[0]
            recovery_days = (recovery_date - max_dd_date).days
        else:
            recovery_date = None
            recovery_days = None
        
        # All drawdowns
        drawdowns = self._find_all_drawdowns(drawdown)
        
        return {
            "max_drawdown": max_drawdown,
            "max_drawdown_date": max_dd_date,
            "recovery_date": recovery_date,
            "recovery_days": recovery_days,
            "avg_drawdown": np.mean([d["depth"] for d in drawdowns]),
            "avg_drawdown_days": np.mean([d["duration"] for d in drawdowns]),
            "drawdowns": drawdowns,
        }
    
    def _find_all_drawdowns(self, drawdown: pd.Series) -> List[Dict]:
        """Find all drawdown periods"""
        is_dd = drawdown < 0
        
        drawdowns = []
        in_drawdown = False
        start_date = None
        max_dd = 0
        
        for date, dd in drawdown.items():
            if dd < 0 and not in_drawdown:
                # Start of drawdown
                in_drawdown = True
                start_date = date
                max_dd = dd
            elif dd < 0 and in_drawdown:
                # Continuing drawdown
                max_dd = min(max_dd, dd)
            elif dd == 0 and in_drawdown:
                # End of drawdown
                in_drawdown = False
                drawdowns.append({
                    "start": start_date,
                    "end": date,
                    "duration": (date - start_date).days,
                    "depth": max_dd,
                })
        
        return drawdowns
      
