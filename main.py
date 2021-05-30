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
