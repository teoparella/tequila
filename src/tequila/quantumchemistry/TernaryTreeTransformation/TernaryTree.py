from openfermion.ops.operators import QubitOperator
from tequila.quantumchemistry.TernaryTreeTransformation.Plant_a_Tree import *
from tequila.quantumchemistry.TernaryTreeTransformation.Tree_Graph import Tree_Graph


def inline_product(factors, seed):
    """
    Args:
        seed (T): The starting total. The unit value.
        factors (iterable[T]): Values to multiply (with *=) into the total.
    Returns:
        T: The result of multiplying all the factors into the unit value.
    """
    for r in factors:
        seed *= r
    return seed


def inline_sum(summands, seed):
    """
    Args:
        seed (T): The starting total. The zero value.
        summands (iterable[T]): Values to add (with +=) into the total.
    Returns:
        T: The result of adding all the factors into the zero value.
    """
    for r in summands:
        seed += r
    return seed



def Ternary_Tree(operator, graph=None, LadderPermutation=None, n_qubits=None):
    
    from openfermion.utils import count_qubits
    
    if n_qubits is None:
        n_qubits = count_qubits(operator)
    if n_qubits < count_qubits(operator):
        raise ValueError('Invalid number of qubits specified.')
    
    # Build the TT.
    Ternary_Tree = PlantTree(n_qubits,graph=graph,LadderPermutation=LadderPermutation) #Tree_Graph()

    # Compute transformed operator.
    transformed_terms = (_transform_operator_term(
        term=term, coefficient=operator.terms[term], Ternary_Tree=Ternary_Tree, LadderPermutation=LadderPermutation)
                         for term in operator.terms)
    return inline_sum(summands=transformed_terms, seed=QubitOperator())


def _transform_operator_term(term, coefficient, Ternary_Tree, LadderPermutation):
    """
    Args:
        term (list[tuple[int, int]]):
            A list of (mode, raising-vs-lowering) ladder operator terms.
        coefficient (float):
        Ternary_Tree (PlantTree):
    Returns:
        QubitOperator:
    """

    transformed_ladder_ops = (_transform_ladder_operator(
        ladder_operator, Ternary_Tree, LadderPermutation) for ladder_operator in term)
    return inline_product(factors=transformed_ladder_ops,
                          seed=QubitOperator((), coefficient))


def _transform_ladder_operator(ladder_operator, Ternary_Tree,LadderPermutation):
    """
    Args:
        ladder_operator (tuple[int, int]):
        Ternary_Tree (PlantTree):
    Returns:
        QubitOperator:
    """
    # The fermion lowering [rasing] operator is given by a = (c+id)/2 [a^\dagger=(c-id)/2] with c, d the majoranas.
    index = ladder_operator[0]
    
    if LadderPermutation != None:
        index=LadderPermutation[index]
        
    current_node=Ternary_Tree.get_node(index)

    #lowering or raising operator:
    
    d_coefficient = -.5j if ladder_operator[1] else .5j
    
    #X,Y,Z Sets for each majorana pairing. Implemented from [arXiv:2212.09731] algorithm 1.
    
    Xset_c=[index]
    Xset_d=[]
    Yset_c=[]
    Yset_d=[index]
    Zset_c=[]
    Zset_d=[]
    
    #Build 'X' descending path for c majorana
    
    if current_node.Xchild != None:
        
        c_node = current_node.Xchild
        
        while c_node.Zchild != None:
            Zset_c.append(c_node.index)
            c_node=c_node.Zchild
            
        Zset_c.append(c_node.index)
    
    #Build 'Y' descending path for d majorana
            
    if current_node.Ychild != None:
        
        d_node = current_node.Ychild
        
        while d_node.Zchild != None:
            Zset_d.append(d_node.index)
            d_node=d_node.Zchild
            
        Zset_d.append(d_node.index)
    
    #Build ascending paths, common for both c,d majoranas
    
    while current_node.parent != None:
            
        if current_node.parent.Xchild == current_node:
            Xset_c.append(current_node.parent.index)
            Xset_d.append(current_node.parent.index)
        
        elif current_node.parent.Ychild == current_node:
            Yset_c.append(current_node.parent.index)
            Yset_d.append(current_node.parent.index)
        
        elif current_node.parent.Zchild == current_node:
            Zset_c.append(current_node.parent.index)
            Zset_d.append(current_node.parent.index)
        
        current_node = current_node.parent
    
    #Compute paired majoranas 
    
    c_majorana_component = QubitOperator((tuple((index, 'X') for index in Xset_c)+ tuple((index, 'Y') for index in Yset_c) + tuple((index, 'Z') for index in Zset_c)), 0.5)
    d_majorana_component = QubitOperator((tuple((index, 'X') for index in Xset_d)+ tuple((index, 'Y') for index in Yset_d) + tuple((index, 'Z') for index in Zset_d)), d_coefficient)
    
    return c_majorana_component + d_majorana_component


