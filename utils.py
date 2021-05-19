import z3, ast, astor, inspect
from contextlib import contextmanager

# *******                                                                                               *******
# *******       SAME AS FUZZING BOOK CODE (CHECK BELOW TO SEE WHERE CHANGES IN THIS FILE STARTED)       *******
# *******                                                                                               *******

MAX_DEPTH = 100
MAX_TRIES = 100
MAX_ITER = 100

SYM_VARS = {
    int: (
        z3.Int, z3.IntVal), float: (
            z3.Real, z3.RealVal), str: (
                z3.String, z3.StringVal)}

SYM_VARS_STR = {
    k.__name__: ("z3.%s" % v1.__name__, "z3.%s" % v2.__name__)
    for k, (v1, v2) in SYM_VARS.items()
}

Function_Summaries = {}
Function_Summaries['func_name'] = {
        'predicate': "",
        'vars': {}}

@contextmanager
def checkpoint(z3solver):
    z3solver.push()
    yield z3solver
    z3solver.pop()

def used_vars(fn):
    return declarations(ast.parse(inspect.getsource(fn)))

def translate_to_z3_name(v):
    return SYM_VARS_STR[v][0]

def define_symbolic_vars(fn_vars, prefix):
    sym_var_dec = ', '.join([prefix + n for n in fn_vars])
    sym_var_def = ', '.join(["%s('%s%s')" % (t, prefix, n)
                             for n, t in fn_vars.items()])
    return "%s = %s" % (sym_var_dec, sym_var_def)

def used_identifiers(src):
    def names(astnode):
        lst = []
        if isinstance(astnode, ast.BoolOp):
            for i in astnode.values:
                lst.extend(names(i))
        elif isinstance(astnode, ast.BinOp):
            lst.extend(names(astnode.left))
            lst.extend(names(astnode.right))
        elif isinstance(astnode, ast.UnaryOp):
            lst.extend(names(astnode.operand))
        elif isinstance(astnode, ast.Call):
            for i in astnode.args:
                lst.extend(names(i))
        elif isinstance(astnode, ast.Compare):
            lst.extend(names(astnode.left))
            for i in astnode.comparators:
                lst.extend(names(i))
        elif isinstance(astnode, ast.Name):
            lst.append(astnode.id)
        elif isinstance(astnode, ast.Expr):
            lst.extend(names(astnode.value))
        elif isinstance(astnode, (ast.Num, ast.Str, ast.Tuple, ast.NameConstant)):
            pass
        elif isinstance(astnode, ast.Assign):
            for t in astnode.targets:
                lst.extend(names(t))
            lst.extend(names(astnode.value))
        elif isinstance(astnode, ast.Module):
            for b in astnode.body:
                lst.extend(names(b))
        else:
            raise Exception(str(astnode))
        return list(set(lst))
    return names(ast.parse(src))

def to_src(astnode):
    return astor.to_source(astnode).strip()

# *******                                               *******
# *******       SOME CHANGES IN FUZZING BOOK CODE       *******
# *******                                               *******

# ASSERTION ERROR FOR UNSATISFIED CORES REMOVED
# SUPPORT FOR LIST ADDED
def declarations(astnode, hm=None):
    if hm is None:
        hm = {}
    if isinstance(astnode, ast.Module):
        for b in astnode.body:
            declarations(b, hm)
    elif isinstance(astnode, ast.FunctionDef):
        #hm[astnode.name + '__return__'] = translate_to_z3_name(astnode.returns.id)
        for a in astnode.args.args:
            hm[a.arg] = translate_to_z3_name(a.annotation.id)
        for b in astnode.body:
            declarations(b, hm)
    elif isinstance(astnode, ast.Call):
        # get declarations from the function summary.
        n = astnode.function
        assert isinstance(n, ast.Name)  # for now.
        name = n.id
        hm.update(dict(Function_Summaries[name]['vars']))
    elif isinstance(astnode, ast.AnnAssign):
        assert isinstance(astnode.target, ast.Name)
        if isinstance(astnode.value, ast.List): # ADDED BY US
            if isinstance(astnode.value.elts[0], ast.Num):
                etype = type(astnode.value.elts[0].n)
            else:
                etype = type(astnode.value.elts[0].s)
            for i in range(0, len(astnode.value.elts)):
                hm[f"{astnode.target.id}_{i}"] = translate_to_z3_name(etype.__name__)
        else:
            hm[astnode.target.id] = translate_to_z3_name(astnode.annotation.id)
    elif isinstance(astnode, ast.Assign):
        if not isinstance(astnode.targets[0], ast.Subscript): # ADDED BY US
            for t in astnode.targets:
                assert isinstance(t, ast.Name)
                assert t.id in hm
    elif isinstance(astnode, ast.AugAssign):
        assert isinstance(astnode.target, ast.Name)
        assert astnode.target.id in hm
    elif isinstance(astnode, (ast.If, ast.For, ast.While)):
        for b in astnode.body:
            declarations(b, hm)
        for b in astnode.orelse:
            declarations(b, hm)
    elif isinstance(astnode, ast.Return):
        pass
    else:
        return {}
        # raise Exception(to_src(astnode))
    return hm

# SUPPORT FOR LIST ADDED
def identifiers_with_types(identifiers, defined):
    with_types = dict(defined)
    for i in identifiers:
        if i[0] == '_':
            if i.count('_') > 2: # THIS IF IS ADDED BY US
                l = i.rfind('_')
                name = i[1:l]
            else:
                nxt = i[1:].find('_', 1)
                name = i[1:nxt + 1]
            assert name in defined
            typ = defined[name]
            with_types[i] = typ
    return with_types

# SUPPORT FOR LIST ADDED
def rename_variables(astnode, env):
    if isinstance(astnode, ast.BoolOp):
        fn = 'z3.And' if isinstance(astnode.op, ast.And) else 'z3.Or'
        return ast.Call(
            ast.Name(fn, None),
            [rename_variables(i, env) for i in astnode.values], [])
    elif isinstance(astnode, ast.BinOp):
        return ast.BinOp(
            rename_variables(astnode.left, env), astnode.op,
            rename_variables(astnode.right, env))
    elif isinstance(astnode, ast.UnaryOp):
        if isinstance(astnode.op, ast.Not):
            return ast.Call(
                ast.Name('z3.Not', None),
                [rename_variables(astnode.operand, env)], [])
        else:
            return ast.UnaryOp(astnode.op,
                               rename_variables(astnode.operand, env))
    elif isinstance(astnode, ast.Call):
        return ast.Call(astnode.func,
                        [rename_variables(i, env) for i in astnode.args],
                        astnode.keywords)
    elif isinstance(astnode, ast.Compare):
        return ast.Compare(
            rename_variables(astnode.left, env), astnode.ops,
            [rename_variables(i, env) for i in astnode.comparators])
    elif isinstance(astnode, ast.Name):
        if astnode.id not in env:
            env[astnode.id] = 0
        num = env[astnode.id]
        return ast.Name('_%s_%d' % (astnode.id, num), astnode.ctx)
    elif isinstance(astnode, ast.Subscript): # THIS ELIF IS ADDED BY US
        id = to_src(astnode)
        name = id[:-3] + '_' + id[-2]
        if name not in env:
            env[name] = 0
        num = env[name]
        return ast.Name('_%s_%d' % (name, num), astnode.ctx)
    elif isinstance(astnode, ast.Return):
        return ast.Return(rename_variables(astnode.value, env))
    else:
        return astnode

# ASSERTION ERROR FOR UNSATISFIED CORES REMOVED
# SUPPORT FOR LIST (BOTH ANNOTATED AND NON-ANNOTATED) ADDED
def to_single_assignment_predicates(path):
    env = {}
    new_path = []
    completed_path = False
    for i, node in enumerate(path):
        ast_node = node.cfgnode.ast_node
        new_node = None
        if isinstance(ast_node, ast.AnnAssign) and ast_node.target.id in {
                'exit'}:
            completed_path = True
            new_node = None
        elif isinstance(ast_node, ast.AnnAssign) and ast_node.target.id in {'enter'}:
            args = [
                ast.parse(
                    "%s == _%s_0" %
                    (a.id, a.id)).body[0].value for a in ast_node.annotation.args]
            new_node = ast.Call(ast.Name('z3.And', None), args, [])
        elif isinstance(ast_node, ast.AnnAssign) and ast_node.target.id in {'_if', '_while'}:
            new_node = rename_variables(ast_node.annotation, env)
            if node.order != 0:
                # assert node.order == 1 # WE COMMENTED THIS ASSERTION OUT
                if node.order != 1:
                    return [], False
                new_node = ast.Call(ast.Name('z3.Not', None), [new_node], [])
        elif isinstance(ast_node, ast.Assign): # THIS ELIF IS ADDED BY US
            if isinstance(ast_node.targets[0], ast.Subscript):
                identifier = to_src(ast_node.targets[0])
                assigned = identifier[:-3] + '_' + identifier[-2]
                value = [rename_variables(ast_node.value, env)]
                env[assigned] = 0 if assigned not in env else env[assigned] + 1
                target = ast.Name('_%s_%d' % (assigned, env[assigned]), None)
            else:
                assigned = ast_node.targets[0].id
                value = [rename_variables(ast_node.value, env)]
                env[assigned] = 0 if assigned not in env else env[assigned] + 1
                target = ast.Name('_%s_%d' % (assigned, env[assigned]), None)
            new_node = ast.Expr(ast.Compare(target, [ast.Eq()], value))
        elif isinstance(ast_node, ast.AnnAssign): # THIS ELIF IS ADDED BY US
            if isinstance(ast_node.value, ast.List):
                for i, element in enumerate(ast_node.value.elts):
                    assigned = ast_node.target.id + "_" + str(i)
                    value = [rename_variables(element, env)]
                    env[assigned] = 0
                    target = ast.Name('_%s_%d' % (assigned, env[assigned]), None)
                    new_path.append(ast.Expr(ast.Compare(target, [ast.Eq()], value)))
                pass
            else:
                assigned = ast_node.target.id
                value = [rename_variables(ast_node.value, env)]
                env[assigned] = 0 if assigned not in env else env[assigned] + 1
                target = ast.Name('_%s_%d' % (assigned, env[assigned]), None)
                new_node = ast.Expr(ast.Compare(target, [ast.Eq()], value))
        elif isinstance(ast_node, (ast.Return, ast.Pass)):
            new_node = None
        else:
            continue
            # s = "NI %s %s" % (type(ast_node), ast_node.target.id) # WE COMMENTED THIS ASSERTION OUT
            # raise Exception(s)
        new_path.append(new_node)
    return new_path, completed_path