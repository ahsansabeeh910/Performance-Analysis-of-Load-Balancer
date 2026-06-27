"""Performance metrics collector and analyzer."""
import numpy as np
from typing import List, Dict
from simulation.request import Request
from simulation.server import Server


class MetricsCollector:
    """Collects and computes performance metrics from simulation results.
    
    Analyzes completed requests and server states to compute:
    - Response Time statistics (avg, min, max, p95)
    - Throughput (requests per second)
    - Server Utilization (per-server and average)
    - Load Distribution Efficiency (standard deviation of request counts)
    """

    def __init__(self, requests: List[Request], servers: List[Server],
                 simulation_time: float):
        self.requests = requests
        self.servers = servers
        self.simulation_time = simulation_time

    def compute_all(self) -> Dict:
        """Compute all performance metrics.
        
        Returns:
            Dictionary containing all computed metrics
        """
        return {
            'response_time': self.compute_response_time(),
            'throughput': self.compute_throughput(),
            'server_utilization': self.compute_server_utilization(),
            'load_distribution': self.compute_load_distribution(),
        }

    def compute_response_time(self) -> Dict:
        """Compute response time statistics.
        
        Returns:
            Dictionary with avg, min, max, p95, and median response times
        """
        if not self.requests:
            return {'avg': 0, 'min': 0, 'max': 0, 'p95': 0, 'median': 0}
        
        response_times = np.array([r.response_time for r in self.requests])
        return {
            'avg': float(np.mean(response_times)),
            'min': float(np.min(response_times)),
            'max': float(np.max(response_times)),
            'p95': float(np.percentile(response_times, 95)),
            'median': float(np.median(response_times)),
        }

    def compute_throughput(self) -> Dict:
        """Compute throughput metrics.
        
        Returns:
            Dictionary with total requests, simulation time, and requests/sec
        """
        if self.simulation_time <= 0:
            return {'total_requests': 0, 'simulation_time': 0, 'requests_per_sec': 0}
        
        return {
            'total_requests': len(self.requests),
            'simulation_time': float(self.simulation_time),
            'requests_per_sec': float(len(self.requests) / self.simulation_time),
        }

    def compute_server_utilization(self) -> Dict:
        """Compute per-server and average utilization.
        
        Returns:
            Dictionary with per-server utilization list and average utilization
        """
        utilizations = []
        for server in self.servers:
            util = server.get_utilization(self.simulation_time)
            utilizations.append({
                'server_id': server.id,
                'utilization': util,
                'total_requests': server.total_requests,
                'weight': server.weight,
            })
        
        avg_util = float(np.mean([u['utilization'] for u in utilizations])) if utilizations else 0
        
        return {
            'per_server': utilizations,
            'average': avg_util,
        }

    def compute_load_distribution(self) -> Dict:
        """Compute load distribution efficiency.
        
        A lower standard deviation means more even distribution.
        The efficiency score is calculated as 1 - (normalized std deviation).
        
        Returns:
            Dictionary with per-server request counts, std deviation,
            coefficient of variation, and efficiency score
        """
        request_counts = np.array([s.total_requests for s in self.servers])
        
        if len(request_counts) == 0 or np.sum(request_counts) == 0:
            return {
                'per_server_requests': [],
                'std_deviation': 0,
                'coefficient_of_variation': 0,
                'efficiency_score': 100.0,
            }
        
        std = float(np.std(request_counts))
        mean = float(np.mean(request_counts))
        cv = float(std / mean) if mean > 0 else 0
        
        # Efficiency score: 100% = perfectly even, lower = more uneven
        efficiency = max(0, (1 - cv) * 100)
        
        return {
            'per_server_requests': request_counts.tolist(),
            'std_deviation': std,
            'coefficient_of_variation': cv,
            'efficiency_score': float(efficiency),
        }

    def get_summary(self) -> Dict:
        """Get a summary of key metrics for display in the results table.
        
        Returns:
            Dictionary with key metrics formatted for table display
        """
        metrics = self.compute_all()
        return {
            'avg_response_time': round(metrics['response_time']['avg'], 4),
            'p95_response_time': round(metrics['response_time']['p95'], 4),
            'throughput': round(metrics['throughput']['requests_per_sec'], 2),
            'avg_utilization': round(metrics['server_utilization']['average'], 2),
            'load_efficiency': round(metrics['load_distribution']['efficiency_score'], 2),
        }
