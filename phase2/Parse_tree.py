class Node:
    def __init__(self, name, parent) -> None:
        self.name = name
        self.parent = parent
        self.childs = []

    def add_child(self, child):
        self.childs.insert(0, child)


class Parse_tree:
    def __init__(self) -> None:
        self.start = Node('Program', None)
        self.nodes = [self.start]

    def print_status(self):
        # print('***status****')
        for n in self.nodes:
            print(n.name, end='\t')
        # print()
        # print('************')