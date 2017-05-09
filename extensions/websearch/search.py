name = 'WebSearch'
icon = 'web-browser'

def main(query):
    if query.startswith('google=') or query.startswith('g='):
        label = 'Search Google: '
        infos = compose_url(query, 'https://google.com/search?q=')
        return (label + infos[1], icon, 'firefox "' + infos[0] + '"')
    elif query.startswith('wikipedia=') or query.startswith('w=') or query.startswith('wiki='):
        label = 'Search Wikipedia: '
        infos = compose_url(query, 'https://en.wikipedia.org/wiki/')
        return (label + infos[1], icon, 'firefox "' + infos[0] + '"')
    elif query.startswith('stackoverflow') or query.startswith('so='):
        label = 'Search Stack Overflow: '
        infos = compose_url(query, 'http://stackoverflow.com/search?q=')
        return (label + infos[1], icon, 'firefox "' + infos[0] + '"')
    elif query.startswith('duckduckgo=') or query.startswith('ddg='):
        label = 'Search Duck Duck Go: '
        infos = compose_url(query, 'https://duckduckgo.com/?q=')
        return (label + infos[1], icon, 'firefox "' + infos[0] + '"')
    else:
        return 0
        
def compose_url(query, url):
    search = query.split('=')[1]
    url = url + search
    return (url, search)

#    if not os.path.exists(CACHE_DIR):
#        os.makedirs(CACHE_DIR)
