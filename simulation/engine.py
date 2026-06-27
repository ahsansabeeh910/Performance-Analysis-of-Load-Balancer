"""SimPy-based simulation engine for load balancer performance analysis."""
import simpy
import numpy as np
from typing import List, Dict, Optional, Callable
from .server import Server
from .request import Request
from .load_balancer import LoadBalancer


class SimulationEngine:
    """Orchestrates the discrete-event simulation of load balancing.
    
    Creates a SimPy environment, generates requests at configurable
    arrival rates, distributes them using the specified algorithm,
    and collects performance data.
    
    Attributes:
        num_servers: Number of servers in the simulation
        num_requests: Total number of requests to generate
        arrival_rate: Average requests per second (Poisson process)
        service_rate: Average service rate per server
        algorithm: Load balancing algorithm name
        server_weights: Per-server weights (for Weighted Round Robin)
        server_capacity: Number of concurrent requests per server
    """

    def __init__(self, num_servers: int = 3, num_requests: int = 100,
                 arrival_rate: float = 10.0, service_rate: float = 5.0,
                 algorithm: str = "Round Robin",
                 server_weights: Optional[List[int]] = None,
                 server_capacity: int = 1,
                 progress_callback: Optional[Callable[[int, int], None]] = None):
        self.num_servers = num_servers
        self.num_requests = num_requests
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.algorithm = algorithm
        self.server_weights = server_weights or [1] * num_servers
        self.server_capacity = server_capacity
        self.progress_callback = progress_callback
        
        # Simulation state
        self.env: Optional[simpy.Environment] = None
        self.servers: List[Server] = []
        self.load_balancer: Optional[LoadBalancer] = None
        self.completed_requests: List[Request] = []
        self.simulation_time: float = 0.0

    def run(self) -> Dict:
        """Run the simulation and return results.
        
        Returns:
            Dictionary containing:
            - 'requests': List of completed Request objects
            - 'servers': List of Server objects with stats
            - 'simulation_time': Total simulation duration
            - 'algorithm': Algorithm name used
        """
        # Set random seed based on algorithm for reproducibility within a run
        # but allow different algorithms to show different behavior
        self.env = simpy.Environment()
        
        # Create servers with configured weights
        self.servers = []
        for i in range(self.num_servers):
            weight = self.server_weights[i] if i < len(self.server_weights) else 1
            server = Server(self.env, server_id=i, weight=weight,
                          capacity=self.server_capacity)
            self.servers.append(server)
        
        # Create load balancer
        self.load_balancer = LoadBalancer(self.servers, self.algorithm)
        
        # Reset completed requests
        self.completed_requests = []
        
        # Start request generator process
        self.env.process(self._generate_requests())
        
        # Run simulation
        self.env.run()
        
        self.simulation_time = self.env.now
        
        return {
            'requests': self.completed_requests,
            'servers': self.servers,
            'simulation_time': self.simulation_time,
            'algorithm': self.algorithm
        }

    def _generate_requests(self):
        """SimPy process that generates requests with Poisson arrivals.
        
        Uses exponential inter-arrival times to simulate a Poisson process.
        Each request is assigned to a server and processed concurrently.
        """
        for i in range(self.num_requests):
            # Exponential inter-arrival time (Poisson process)
            inter_arrival = np.random.exponential(1.0 / self.arrival_rate)
            yield self.env.timeout(inter_arrival)
            
            # Generate service time (exponential distribution)
            service_time = np.random.exponential(1.0 / self.service_rate)
            
            # Create request
            request = Request(
                id=i,
                arrival_time=self.env.now,
                service_time=service_time
            )
            
            # Select server and start processing
            server = self.load_balancer.select_server()
            request.assigned_server = server.id
            
            # Start processing in background
            self.env.process(self._process_request(request, server))
            
            # Report progress
            if self.progress_callback:
                self.progress_callback(i + 1, self.num_requests)

    def _process_request(self, request: Request, server: Server):
        """SimPy process that handles a single request on a server.
        
        Args:
            request: The request to process
            server: The server to process it on
        """
        with server.resource.request() as req:
            yield req
            
            # Record start time
            request.start_time = self.env.now
            server.active_connections += 1
            server.total_requests += 1
            
            # Process request
            yield self.env.timeout(request.service_time)
            
            # Record completion
            request.end_time = self.env.now
            server.active_connections -= 1
            server.busy_time += request.service_time
            server.total_service_time += request.service_time
            
            self.completed_requests.append(request)
