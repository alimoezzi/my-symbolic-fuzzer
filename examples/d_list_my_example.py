def d_list_my_example(a: int, b: int, c: int) -> int:
    mylist: list[int] = [2, 5]
    mylist[0] = 4
    if mylist[0] > a:
        return a
    elif mylist[0] > b:
        return b
    else:
        return c