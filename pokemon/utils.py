class FixedFIFO:
    def __init__(self, capacity=3):
        self.capacity = capacity
        self.queue = []

    def push(self, item):
        """Add an item to the FIFO queue."""
        if len(self.queue) >= self.capacity:
            self.queue.pop(0)  # Remove the oldest item
        self.queue.append(item)

    def get_item(self, index):
        """Return the item at a specific index if it exists."""
        if index < 0 or index >= len(self.queue):
            return 'No Memory Exist'  # Index out of bounds
        return self.queue[index]

    def __repr__(self):
        return repr(self.queue)