"""
Trading multiples analysis
"""

from typing import Any, Dict, List


class MultiplesAnalysis:
    """
    Analyze company using trading multiples
    """
    
    def compare_multiples(
        self,
        company: Dict[str, float],
        peers: List[Dict[str, float]],
    ) -> Dict[str, Any]:
        """
        Compare company multiples to peer group
        
        Args:
            company: Company metrics
            peers: List of peer companies metrics
        """
        multiples = ["pe_ratio", "pb_ratio", "ps_ratio", "ev_ebitda"]
        
        comparison = {}
        
        for multiple in multiples:
            company_value = company.get(multiple)
            peer_values = [p.get(multiple) for p in peers if p.get(multiple)]
            
            if peer_values:
                peer_median = sorted(peer_values)[len(peer_values) // 2]
                peer_avg = sum(peer_values) / len(peer_values)
                
                comparison[multiple] = {
                    "company": company_value,
                    "peer_median": peer_median,
                    "peer_average": peer_avg,
                    "premium_discount": (
                        (company_value - peer_median) / peer_median * 100
                        if peer_median and company_value
                        else None
                    ),
                }
        
        return comparison
    
    def implied_value(
        self,
        metric: float,
        multiple: str,
        peer_multiple: float,
    ) -> float:
        """
        Calculate implied value based on peer multiple
        
        Args:
            metric: Company metric (earnings, book value, etc.)
            multiple: Type of multiple
            peer_multiple: Peer group median multiple
        """
        return metric * peer_multiple
    
    def score_valuation(
        self,
        company: Dict[str, float],
        sector_averages: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Score valuation relative to sector
        
        Lower multiples = better value (higher score)
        """
        scores = {}
        
        # P/E score (lower is better)
        pe = company.get("pe_ratio")
        pe_avg = sector_averages.get("pe_ratio", pe)
        if pe and pe_avg:
            scores["pe_score"] = min(100, max(0, (pe_avg / pe) * 50))
        
        # P/B score
        pb = company.get("pb_ratio")
        pb_avg = sector_averages.get("pb_ratio", pb)
        if pb and pb_avg:
            scores["pb_score"] = min(100, max(0, (pb_avg / pb) * 50))
        
        # Dividend yield score (higher is better)
        div_yield = company.get("dividend_yield", 0)
        div_avg = sector_averages.get("dividend_yield", div_yield)
        if div_yield is not None and div_avg:
            scores["dividend_score"] = min(100, (div_yield / div_avg) * 50)
        
        # Overall score
        if scores:
            scores["overall"] = sum(scores.values()) / len(scores)
        
        return scores
      
