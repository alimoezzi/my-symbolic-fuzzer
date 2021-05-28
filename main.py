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
