from MySymbolicFuzzer import MySymbolicFuzzer
import importdir
importdir.do("examples", globals())

def myInput(input_name, type):
    while True:
        user_input = input(f"{input_name}: ")
        try:
            return type(user_input)
        except:
            print(f"{str(user_input)} must be a/an {str(type)}")

if __name__ == "__main__":
    max_depth = myInput("max_depth", int)
    max_tries = myInput("max_tries", int)
    max_iter = myInput("max_iter", int)
    example_program = myInput("example_program", str)
    function_name = myInput(f"function from {example_program} program", str)

    msymfz_ = MySymbolicFuzzer(eval(f"{example_program}.{function_name}"), max_depth=max_depth, max_tries=max_tries,max_iter=max_iter)
    paths = msymfz_.get_all_paths(msymfz_.fnenter)

    used_constraint = []
    path_number = 0
    for i in range(len(paths)):
        constraint = msymfz_.extract_constraints(paths[i].get_path_to_root())
        constraint_key = ' '.join(constraint)
        if constraint_key in used_constraint or len(constraint) < 2:
            continue
        used_constraint.append(constraint_key)
        path_number = path_number + 1
        print(f"\n******* Path #{str(path_number)} *******")
        print(f"Contraint Path: {constraint}")
        solution, unsat = msymfz_.solve_constraint(constraint, paths[i].get_path_to_root())
        if unsat:
            continue
        else:
            print(f"Contraint Arguments: {solution}")