name = 'Math'

def main(query):
    if query.startswith('='):
        return (eval(query[1:]), 'gnome-calculator', 'gnome-calculator')
    else:
        return 0
