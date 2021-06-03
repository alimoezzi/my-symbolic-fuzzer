# Symbolic Fuzzer

A symbolic fuzzer that can generate input values symbolically with the following assumptions:

- No recursion
- All variables are annotated with the type information
- The only container used in programs are list of integers with a maximum size of 10

The key idea is as follows: We traverse through the control flow graph from the entry point, and generate all possible paths to a given depth. Then we collect constraints that we encountered along the path, and generate inputs that will traverse the program up to that point.

This tool can:

- Generate and print the path constraints in the program.
- trace each constraint to the part of code that created the constraint.
- Generate the corresponding unsat core and the statements related to an unsatisfiable path.

We used the symbolic fuzzer that is available at [The fuzzing book](https://www.fuzzingbook.org/html/SymbolicFuzzer.html) as the basis of our tool.

## Getting Started

- `git clone https://github.com/realsarm/my-symbolic-fuzzer.git`
- `cd .\my-symbolic-fuzzer`
- `python -m venv myvenv`
- `.\myvenv\Scripts\activate.bat`
- `pip install -r requirements.txt`

### Prerequisites

To render the generated DOT source code, you also need to install [Graphviz](https://www.graphviz.org/)([installation procedure for Windows](https://forum.graphviz.org/t/new-simplified-installation-procedure-on-windows/224))

### Installing

- create your `example.py` file in [examples directory](https://github.com/realsarm/my-symbolic-fuzzer/tree/main/examples) (all files of example directory will be imported to `main.py` dynamically using [importdir](https://gitlab.com/aurelien-lourot/importdir)) or use one of the examples that already exist.
- `python main.py`
- The tool will ask for max_depth(e.g 10), max_tries(e.g 10), max_iter(e.g 10), example_program(e.g [a_check_triangle_book_example](https://github.com/realsarm/my-symbolic-fuzzer/tree/main/examples)), and function_from_example_program(e.g [a_check_triangle_book_example](https://github.com/realsarm/my-symbolic-fuzzer/blob/main/examples/a_check_triangle_book_example.py))
- check the result

## Potential Future Extensions

- Function call to self-contained void methods.
