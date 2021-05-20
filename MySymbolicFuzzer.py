import z3
from PNode import PNode
from AdvancedSymbolicFuzzer import AdvancedSymbolicFuzzer
from utils import to_single_assignment_predicates, identifiers_with_types, to_src, used_identifiers , define_symbolic_vars, checkpoint

class MySymbolicFuzzer(AdvancedSymbolicFuzzer):

    # REMOVE ASSERTION ERROR FOR UNSATISFIED CORES
    def extract_constraints(self, path):
        res = []
        generated_paths, completed = to_single_assignment_predicates(path)
        if not completed:
            return []
        for p in generated_paths:
            if p:
                res.append(to_src(p))
        return res
