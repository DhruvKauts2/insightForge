"""
Alert Evaluator - Evaluates alert rules against Elasticsearch data
"""
from loguru import logger
from datetime import datetime
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.utils.elasticsearch_client import es_client
from api.config import ES_INDEX_PATTERN


class AlertEvaluator:
    """Evaluates alert rules and determines if they should trigger"""
    
    def __init__(self):
        self.es = es_client
    
    def evaluate_rule(self, rule: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Evaluate a single alert rule
        
        Args:
            rule: Alert rule dictionary with configuration
            
        Returns:
            Alert result if triggered, None otherwise
        """
        try:
            # Build Elasticsearch query based on rule
            es_query = self._build_query(rule)
            
            # Execute query
            es_response, query_time = self.es.search(
                index=ES_INDEX_PATTERN,
                body=es_query
            )
            
            # Get the count
            log_count = es_response["hits"]["total"]["value"]
            
            # Evaluate condition
            threshold = rule["threshold"]
            condition = rule["condition"]
            
            triggered = self._check_condition(log_count, threshold, condition)
            
            if triggered:
                logger.info(f"Alert rule '{rule['name']}' triggered: {log_count} {condition} {threshold}")
                
                # Get sample logs
                sample_logs = [
                    hit["_source"] for hit in es_response["hits"]["hits"][:5]
                ]
                
                return {
                    "rule_id": rule["id"],
                    "rule_name": rule["name"],
                    "triggered": True,
                    "value": log_count,
                    "threshold": threshold,
                    "condition": condition,
                    "log_count": log_count,
                    "sample_logs": sample_logs,
                    "query_time_ms": query_time
                }
            else:
                logger.debug(f"Alert rule '{rule['name']}' not triggered: {log_count} {condition} {threshold}")
                return None
                
        except Exception as e:
            logger.error(f"Error evaluating rule '{rule.get('name', 'unknown')}': {e}")
            return None
    
    def _build_query(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """Build Elasticsearch query from rule configuration"""
        must_clauses = []
        
        # Text query if provided
        if rule.get("query"):
            must_clauses.append({
                "query_string": {
                    "query": rule["query"]
                }
            })
        
        # Filter by log levels
        if rule.get("levels"):
            must_clauses.append({
                "terms": {"level": rule["levels"]}
            })
        
        # Filter by services
        if rule.get("services"):
            must_clauses.append({
                "terms": {"service": rule["services"]}
            })
        
        # Build final query
        query = {
            "bool": {"must": must_clauses}
        } if must_clauses else {"match_all": {}}
        
        es_query = {
            "query": query,
            "size": 5,  # Get sample logs
            "sort": [{"timestamp": "desc"}]
        }
        
        return es_query
    
    def _check_condition(self, value: float, threshold: float, condition: str) -> bool:
        """Check if condition is met"""
        if condition == "greater_than":
            return value > threshold
        elif condition == "less_than":
            return value < threshold
        elif condition == "equals":
            return value == threshold
        elif condition == "greater_than_or_equal":
            return value >= threshold
        elif condition == "less_than_or_equal":
            return value <= threshold
        else:
            logger.warning(f"Unknown condition: {condition}")
            return False
