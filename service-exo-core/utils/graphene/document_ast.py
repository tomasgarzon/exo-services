def ast_depth(field):
    if field.selection_set is not None:
        step = 1
        if field.name.value in ['edges', 'node']:
            step = 0
        return step + max(map(ast_depth, field.selection_set.selections) if field else 0)
    return 0
