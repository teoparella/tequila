class TTNode:
    """Ternary Tree node."""
    parent = None
    Xchild = None
    Ychild = None
    Zchild = None
    index = None

    def __init__(self, parent, Xchild, Ychild, Zchild, index=None):
        """Ternary Tree node. Single (or None) parent and up to 3 children.
        Args:
            parent: TTNode. The parent node.
            Xchild: TTNode. Node label of the X child TTnode
            Ychild: TTNode. Node label of the Y child TTnode
            Zchild: TTNode. Node label of the Z child TTnode
            index: Int. Node label.
        """
        self.Xchild = Xchild
        self.Ychild = Ychild
        self.Zchild = Zchild
        self.parent = parent
        self.index = index

    def get_ancestors(self):
        """Returns a list of ancestors of the node. Ordered from the earliest.
        Returns: ancestor_list: A list of TTNodes.
        """
        node = self
        ancestor_list = []
        while node.parent is not None:
            ancestor_list.append(node.parent)
            node = node.parent

        return ancestor_list



class PlantTree:

    def __init__(self, n_qubits, graph=None, LadderPermutation=None):
        """Builds a TT on n_qubits qubits and given graph structure.
        Args:
            n_qubits: Int, the number of qubits in the system
            graph: list, containing the graph of the tree to be planted
        """
        self.nodes = [TTNode(parent=None, Xchild=None, Ychild=None, Zchild=None, index=_) for _ in range(n_qubits)]
        self.LadderPermutation=LadderPermutation

        if n_qubits > 0:
            self.root = self.nodes[graph[0]]
            self.root.index = graph[0]

        def ternary(graph_structure, father):
            """This inner function is used to build the TT on nodes.
                Xbranch: Int. Root of the upcoming X branch.
                Ybranch: Int. Root of the upcoming Y branch.
                Zbranch: Int. Root of the upcoming Z branch.
                parent: Parent node
            """
            #Given the initial graph_structure, iterate on the 3 legs fo the current root.
            for i in range(3):
                Curr_child_branch=graph_structure[1][i] #Cycle of life. Child becomes parent (Root of the upcoming graph)
                if Curr_child_branch!= [None]: #Repeat iteratively until reaching the leafs
                    child=self.nodes[Curr_child_branch[0]]
                    if i==0:
                        father.Xchild=child
                        child.parent=father
                        ternary(Curr_child_branch, child)
                    elif i==1:
                        father.Ychild=child
                        child.parent=father
                        ternary(Curr_child_branch, child)
                    elif i==2:
                        father.Zchild=child
                        child.parent=father
                        ternary(Curr_child_branch, child)
            return
        
        ternary(graph_structure=graph, father=self.root)


    def get_node(self, j:int):
        """Returns the node j.
        Args:
            j (int): Fermionic site index.
        Returns:
            FenwickNode: the node at j.
        """
        return self.nodes[j]
    


    def get_children_set(self, j:int):
        """Returns the children set of j-th node.
        Args:
            j (int): Fermionic site index.
        Returns:
            A list [Xchld,Ychild,Zchild] of children from j.
        """
        node = self.get_node(j)
        
        return [node.Xchild,node.Ychild,node.Zchild]
    