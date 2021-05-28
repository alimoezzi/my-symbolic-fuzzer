def myInput(input_name, type):
    while True:
        user_input = input(f"{input_name}: ")
        try:
            return type(user_input)
        except:
            print(f"{str(user_input)} must be a/an {str(type)}")

