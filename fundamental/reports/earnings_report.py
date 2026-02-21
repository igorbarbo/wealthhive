"""
Earnings report analysis
"""

from typing import Any, Dict


class EarningsReportAnalyzer:
    """
    Analyze quarterly/annual earnings reports
    """
    
    def analyze(
        self,
        current_quarter: Dict[str, float],
        previous_quarter: Dict[str, float],
        same_quarter_last_year: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Analyze earnings report
        
        Compares QoQ and YoY performance
        """
        analysis = {
            "revenue": self._analyze_metric(
                current_quarter.get("revenue"),
                previous_quarter.get("revenue"),
                same_quarter_last_year.get("revenue"),
            ),
            "eps": self._analyze_metric(
                current_quarter.get("eps"),
                previous_quarter.get("eps"),
                same_quarter_last_year.get("eps"),
            ),
            "operating_income": self._analyze_metric(
                current_quarter.get("operating_income"),
                previous_quarter.get("operating_income"),
                same_quarter_last_year.get("operating_income"),
            ),
        }
        
        # Overall assessment
        beats = sum(1 for m in analysis.values() if m.get("beat_expectations"))
        analysis["summary"] = {
            "metrics_beat": beats,
            "total_metrics": len(analysis),
            "assessment": "Strong" if beats >= 2 else "Mixed" if beats == 1 else "Weak",
        }
        
        return analysis
    
    def _analyze_metric(
        self,
        current: float,
        previous: float,
        year_ago: float,
    ) -> Dict[str, Any]:
        """Analyze single metric"""
        if not all([current, previous, year_ago]):
            return {"error": "Insufficient data"}
        
        qoq_change = (current - previous) / previous
        yoy_change = (current - year_ago) / year_ago
        
        return {
            "current": current,
            "qoq_change": round(qoq_change * 100, 2),
            "yoy_change": round(yoy_change * 100, 2),
            "trend": "improving" if qoq_change > 0 else "declining",
            "beat_expectations": qoq_change > 0 and yoy_change > 0,
        }
    
    def generate_summary(self, analysis: Dict) -> str:
        """Generate text summary"""
        summary = analysis.get("summary", {})
        
        text = f"Earnings Analysis: {summary.get('assessment', 'N/A')} quarter\n\n"
        
        for metric, data in analysis.items():
            if metric != "summary":
                text += f"{metric.upper()}: "
                if "error" not in data:
                    text += f"YoY {data['yoy_change']:+.1f}%, QoQ {data['qoq_change']:+.1f}%\n"
                else:
                    text += "Data unavailable\n"
        
        return text
      
