


class SearchSpace:

    def __init__(self):
        self.search_space = {}

    def add_node(self, node):
        self.search_space[node.key] = node

    def get_node(self, key):
        return self.search_space[key]
