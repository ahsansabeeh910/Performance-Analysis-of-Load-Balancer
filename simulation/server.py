"""Server model for load balancer simulation."""
import simpy


class Server:
    """Represents a server in the load balancing simulation.
    
    Each server is modeled as a SimPy Resource with a given capacity.
    It tracks performance statistics like active connections, total
    requests processed, and busy time for utilization calculation.
    
    Attributes:
        id: Unique server identifier
        weight: Server weight for weighted algorithms (higher = more capacity)
        capacity: Number of concurrent requests the server can handle
        active_connections: Current number of requests being processed
        total_requests: Total number of requests processed
        busy_time: Total time the server spent processing requests
    """

    def __init__(self, env: simpy.Environment, server_id: int, 
                 weight: int = 1, capacity: int = 1):
        self.env = env
        self.id = server_id
        self.weight = weight
        self.capacity = capacity
        self.resource = simpy.Resource(env, capacity=capacity)
        
        # Performance tracking
        self.active_connections = 0
        self.total_requests = 0
        self.busy_time = 0.0
        self.total_service_time = 0.0
        self._request_log = []  # List of (start_time, end_time)

    def process_request(self, service_time: float):
        """Process a request with the given service time.
        
        This is a SimPy generator that requests the server resource,
        processes for the given duration, and updates statistics.
        
        Args:
            service_time: Time required to process the request
        """
        with self.resource.request() as req:
            yield req
            start = self.env.now
            self.active_connections += 1
            self.total_requests += 1
            
            yield self.env.timeout(service_time)
            
            end = self.env.now
            self.active_connections -= 1
            self.busy_time += service_time
            self.total_service_time += service_time
            self._request_log.append((start, end))

    def get_utilization(self, total_time: float) -> float:
        """Calculate server utilization as a percentage.
        
        Args:
            total_time: Total simulation duration
            
        Returns:
            Utilization percentage (0-100)
        """
        if total_time <= 0:
            return 0.0
        return min((self.busy_time / (total_time * self.capacity)) * 100, 100.0)
