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

    # ROLLED BACK TO THE VERSION BEFORE EXERCISE 2 "Statically checking if a loop should be unrolled further" FROM FUZZING BOOK
    def get_all_paths(self, fenter):
        path_lst = [PNode(0, fenter)]
        completed = []
        for i in range(self.max_iter):
            new_paths = [PNode(0, fenter)]
            for path in path_lst:
                # explore each path once
                if path.cfgnode.children:
                    np = path.explore()
                    for p in np:
                        if path.idx > self.max_depth:
                            break
                        new_paths.append(p)
                else:
                    completed.append(path)
            path_lst = new_paths
        return completed + path_lst
