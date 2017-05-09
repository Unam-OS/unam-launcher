name = 'RunCmd'
icon = 'gnome-terminal'

def main(query):
    if query.startswith('cmd=') or query.startswith('c=') or query.startswith('command='):
        command = query.split('=')
        return 'Run command: ' + command[1], icon, '"' + command[1] + '"'
    else:
        return 0
