def e_while_loop_my_example(a: int, b: int):
    while(a > b):
        a = a * 2
        b = b - 2
        if a == a ** 2:
            return True
    return False