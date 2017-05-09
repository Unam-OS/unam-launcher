name = 'Notify'
icon = 'notification-new-symbolic'

def main(query):
    if query.startswith('notify=') or query.startswith('n='):
        infos = query[2:].split(':')
        if len(infos) == 2:
            cmd = "sleep " + infos[1] + '&& notify-send -i preferences-desktop-notification-bell "Custom Alert" "' + infos[0] + '"'
            return 'Program notification: ' + infos[0], icon, cmd
        else:
            return 'Program notification: ' + query[2:], icon, 'echo "invialid command"'
    else:
        return 0
