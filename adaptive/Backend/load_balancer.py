import random
from collections import deque

class LoadBalancer:
    def __init__(self, servers):
        self.servers = servers
        self.server_queue = deque(servers)

    def get_server(self):
        if not self.server_queue:
            self.server_queue = deque(self.servers)
        return self.server_queue.popleft()

    def add_server(self, server):
        if server not in self.servers:
            self.servers.append(server)
            self.server_queue.append(server)

    def remove_server(self, server):
        if server in self.servers:
            self.servers.remove(server)
            self.server_queue = deque(s for s in self.server_queue if s != server)

class RoundRobinLoadBalancer(LoadBalancer):
    pass  # The base LoadBalancer already implements Round Robin

class RandomLoadBalancer(LoadBalancer):
    def get_server(self):
        return random.choice(self.servers)

class LeastConnectionsLoadBalancer(LoadBalancer):
    def __init__(self, servers):
        super().__init__(servers)
        self.connections = {server: 0 for server in servers}

    def get_server(self):
        server = min(self.connections, key=self.connections.get)
        self.connections[server] += 1
        return server

    def release_server(self, server):
        if server in self.connections:
            self.connections[server] = max(0, self.connections[server] - 1)

# Example usage
if __name__ == "__main__":
    servers = ["server1", "server2", "server3"]
    
    print("Round Robin Load Balancer:")
    lb = RoundRobinLoadBalancer(servers)
    for _ in range(5):
        print(lb.get_server())

    print("\nRandom Load Balancer:")
    lb = RandomLoadBalancer(servers)
    for _ in range(5):
        print(lb.get_server())

    print("\nLeast Connections Load Balancer:")
    lb = LeastConnectionsLoadBalancer(servers)
    for _ in range(5):
        server = lb.get_server()
        print(server)
        if _ % 2 == 0:
            lb.release_server(server)
