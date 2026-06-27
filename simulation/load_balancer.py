"""Load balancing algorithms for distributing requests across servers."""
from typing import List
from .server import Server


class LoadBalancer:
    """Implements multiple load balancing algorithms.
    
    Supports:
    - Round Robin: Cycles through servers sequentially
    - Least Connections: Picks the server with fewest active connections
    - Weighted Round Robin: Distributes proportionally to server weights
    
    Attributes:
        servers: List of available servers
        algorithm: Name of the current algorithm
    """

    ALGORITHMS = ["Round Robin", "Least Connections", "Weighted Round Robin"]

    def __init__(self, servers: List[Server], algorithm: str = "Round Robin"):
        self.servers = servers
        self.algorithm = algorithm
        
        # Round Robin state
        self._rr_index = 0
        
        # Weighted Round Robin state
        self._wrr_index = 0
        self._wrr_current_weight = 0
        self._wrr_max_weight = max(s.weight for s in servers) if servers else 1
        self._wrr_gcd_weight = self._gcd_list([s.weight for s in servers]) if servers else 1

    def select_server(self) -> Server:
        """Select the next server based on the configured algorithm.
        
        Returns:
            The selected Server instance
        """
        if self.algorithm == "Round Robin":
            return self._round_robin()
        elif self.algorithm == "Least Connections":
            return self._least_connections()
        elif self.algorithm == "Weighted Round Robin":
            return self._weighted_round_robin()
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")

    def _round_robin(self) -> Server:
        """Select server using Round Robin algorithm.
        
        Cycles through servers sequentially, wrapping around at the end.
        """
        server = self.servers[self._rr_index % len(self.servers)]
        self._rr_index += 1
        return server

    def _least_connections(self) -> Server:
        """Select server using Least Connections algorithm.
        
        Picks the server with the fewest active connections.
        Breaks ties by selecting the server with the lower ID.
        """
        return min(self.servers, key=lambda s: (s.active_connections, s.id))

    def _weighted_round_robin(self) -> Server:
        """Select server using Weighted Round Robin algorithm.
        
        Distributes requests proportionally based on server weights.
        Uses the standard WRR algorithm with GCD optimization.
        """
        n = len(self.servers)
        while True:
            self._wrr_index = (self._wrr_index + 1) % n
            if self._wrr_index == 0:
                self._wrr_current_weight -= self._wrr_gcd_weight
                if self._wrr_current_weight <= 0:
                    self._wrr_current_weight = self._wrr_max_weight
            if self.servers[self._wrr_index].weight >= self._wrr_current_weight:
                return self.servers[self._wrr_index]

    @staticmethod
    def _gcd(a: int, b: int) -> int:
        """Calculate the greatest common divisor of two numbers."""
        while b:
            a, b = b, a % b
        return a

    @staticmethod
    def _gcd_list(values: List[int]) -> int:
        """Calculate the GCD of a list of numbers."""
        from functools import reduce
        return reduce(LoadBalancer._gcd, values)
