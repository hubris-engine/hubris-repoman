
def transform(list : "list", transformFn) -> "list":
    o = []
    for v in list:
        o.append(transformFn(v))
    return o
