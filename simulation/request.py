"""Request model for load balancer simulation."""
from dataclasses import dataclass, field


@dataclass
class Request:
    """Represents a client request in the simulation.
    
    Attributes:
        id: Unique request identifier
        arrival_time: Time the request arrived at the load balancer
        start_time: Time the request started being processed
        end_time: Time the request finished processing
        assigned_server: ID of the server that processed this request
        service_time: Time required to process the request
    """
    id: int
    arrival_time: float
    service_time: float
    start_time: float = 0.0
    end_time: float = 0.0
    assigned_server: int = -1

    @property
    def response_time(self) -> float:
        """Total time from arrival to completion."""
        return self.end_time - self.arrival_time

    @property
    def wait_time(self) -> float:
        """Time spent waiting in queue before processing."""
        return self.start_time - self.arrival_time
