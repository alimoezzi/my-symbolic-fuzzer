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

    # SUPPORT FOR UNSAT CORE ADDED
    def solve_constraint(self, constraints, pNodeList):
        identifiers = [c for i in constraints for c in used_identifiers(i)]  # <- changes
        with_types = identifiers_with_types(identifiers, self.used_variables)  # <- changes
        decl = define_symbolic_vars(with_types, '')
        exec(decl)

        solutions = {}
        with checkpoint(self.z3):
            unsatisfied_path = {}

            for i, constraint in enumerate(constraints):
                unsatisfied_path[z3.Bool('p'+ str(i))] = constraint
                eval(f"self.z3.assert_and_track({constraint},'p{str(i)}')")
            if self.z3.check() != z3.sat:
                print(f"\n--- ERROR: UNSATISFIABLE PATH FOUND ---\n")
                print(f"Unsatisfiable core length: {len(self.z3.unsat_core())}")
                unsatisfied_cores = self.z3.unsat_core()
                print(f"Unsatisfiable cores: ")
                for j, unsatisfied_core in enumerate(unsatisfied_cores):
                    if unsatisfied_core not in unsatisfied_path:
                        continue
                    print(f"\t {j+1} : {unsatisfied_path[unsatisfied_core]}")

                print(f"Unsatisfiable Path: ")
                for node in pNodeList:
                    cfgnode_json = node.cfgnode.to_json()
                    at = cfgnode_json['at']
                    ast = cfgnode_json['ast']
                    print(f"\tLine {at} : {ast}")
                return {}, True
            model = self.z3.model()
            solutions = {d.name(): model[d] for d in model.decls()}
            my_args = {k: solutions.get(k, None) for k in self.fn_args}
        predicate = f"z3.And({','.join([f'{k} == {v}' for k, v in my_args.items() if v is not None])})"
        eval(f"self.z3.add(z3.Not({predicate}))")
        return my_args, False