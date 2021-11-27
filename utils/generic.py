import ntpath

def path_leaf(path):
    if path is None:
        return None
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)