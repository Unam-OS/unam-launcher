#!/usr/bin/python3

import gi
import os
import re
import sys
import threading
import subprocess
import setproctitle

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango, Gio
setproctitle.setproctitle('unam-launcher-service')

# Files
home = os.getenv("HOME") + '/'
applications = '/usr/share/applications/.'
running = home + '.config/unam/unam-launcher/running'
log_file = home + '.config/unam/unam-launcher/logs/log'
conf_file = home + '.config/unam/unam-launcher/config'

gconf = Gio.File.new_for_path(conf_file)
gfile = Gio.File.new_for_path(running)
gapps = Gio.File.new_for_path(applications)

monitor = gfile.monitor_file(Gio.FileMonitorFlags.NONE, None)
conf_changed = gconf.monitor_file(Gio.FileMonitorFlags.NONE, None)
dir_changed = gfile.monitor_directory(Gio.FileMonitorFlags.NONE, None)

#os.system("truncate -s 0 " + running)


def get_screen_size(x, y):
    display = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True,stdout=subprocess.PIPE).communicate()[0]
    display = str(display.rstrip())[2:-1]
    display = display.split('x')
    
    if x == True and y == True:
        return display
    elif x == True and y == False:
        return display[0]
    elif x == False and y == True:
        return display[1]
    elif x == False and y == False:
        return display[0] + 'x' + display[1]

def log(message):
    with open(log_file, "a") as logfile:
        logfile.write(message + '\n')
        
def str2bool(string):
  return string.lower() in ("yes", "true", "t", "1")

class spacer():
    def __init__(self):
        self.box = Gtk.Box()
        self.label = Gtk.Label('')
        self.box.add(self.label)
        
        self.label.set_hexpand(True)
        self.label.set_alignment(0.1,0.5)
        #self.box.set_sensitive(False)
        
    def get_box(self):
        return self.box
        
class extbutton():
    def __init__(self):
        self.box = Gtk.HBox()
        self.label = Gtk.Label()
        self.margin = Gtk.Label('     ')
        self.icon = Gtk.Image()

        self.label.set_hexpand(True)
        self.icon.set_alignment(0,0.5)
        self.label.set_alignment(0,0.5)
        
        self.box.pack_start(self.margin, False, False, 4)        
        self.box.pack_start(self.icon, False, False, 4)
        self.box.pack_start(self.label, True, True, 4)
        
    def set_text(self, text):
        self.label.set_text(text)
        
    def set_font(self, name, size):
        font_name = name + ' ' + str(size)
        NewFont = Pango.FontDescription(font_name)
        self.label.modify_font(NewFont)
        
    def set_icon(self, icon_name, icon_size):
        self.icon.set_from_icon_name(icon_name, icon_size)

    def get_box(self):
        return self.box

class appbutton():
    def __init__(self):
        self.button = Gtk.Button()
        self.label = Gtk.Label()
        self.icon = Gtk.Image()
        self.layoutbox = Gtk.Box()
        self.command = ''
        
        self.build()
        
    def build(self):
        self.flat()
        self.label.set_alignment(0,0.5)
        self.button.set_hexpand(True)
        self.layoutbox.pack_start(self.icon, False, False, 4)
        self.layoutbox.pack_start(self.label, True, True, 4)
        self.button.add(self.layoutbox)
        
    def construct(self, icon_name, label_text, tooltip_text, command):
        self.set_icon(icon_name, Gtk.IconSize.MENU)
        self.set_label(label_text)
        self.set_tooltip(tooltip_text)
        self.set_command(command)
        
    def flat(self):
        classes = self.button.get_style_context()
        classes.add_class('flat')
        
    def on_click(self, button, cmd):
        os.system(cmd + ' &')
        log('App launched: ' + cmd)
        app.invisible(None, None)
        
    def set_icon(self, icon_name, icon_size):
        self.icon.set_from_icon_name(icon_name, icon_size)
        
    def get_icon(self):
        return self.icon.get_from_icon_name()
        
    def set_label(self, text):
        self.label.set_text(text)
        
    def get_label(self):
        return self.label.get_text()
        
    def set_tooltip(self, text):
        self.button.set_tooltip_text(text)
        
    def get_tooltip(self):
        return self.button.get_tooltip_text()
        
    def set_command(self, cmd):
        self.command = cmd
        self.button.connect('clicked', self.on_click, cmd)
        
    def set_font(self, name, size):
        font_name = name + ' ' + str(size)
        NewFont = Pango.FontDescription(font_name)
        self.label.modify_font(NewFont)
        
    def get_command(self):
        return self.command
        
    def get_button(self):
        return self.button
        
    def get_basic_info(self):
        return self.get_label(), self.get_tooltip()
                
    def get_info(self):
        return self.get_label(), self.get_command(), self.get_tooltip() #, self.get_icon()

# Main Program
class launcher(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Unam Launcher")

        log('Started new service thread')

        self.found = False
        self.no_search = True
        self.visible = False
        self.config = conf_changed
        self.trigger = monitor
        self.update = dir_changed
        
        # Extensions
        self.cmdsearch = False
        self.math = False
        self.websearch = False
        self.notify = False
        self.runcmd = False
        
        # keyboard shortcuts
        accel = Gtk.AccelGroup()
        accel.connect(Gdk.keyval_from_name('Q'), Gdk.ModifierType.CONTROL_MASK, 0, Gtk.main_quit)
        self.add_accel_group(accel)

        self.semaphore = threading.Semaphore(4)
        self.wrapper = Gtk.VBox()
        self.scrollbox = Gtk.ScrolledWindow()
        self.scrollframe = Gtk.Viewport()
        self.box = Gtk.Box(spacing=6)   
        self.spacer = Gtk.Box()
        self.search_entry = Gtk.Entry()
        self.app_menu = Gtk.VBox()

        self.connect("delete-event", Gtk.main_quit)
        self.connect('focus-out-event', self.invisible)
        self.connect('key_press_event', self.on_key_press)
        self.trigger.connect("changed", self.toggle_visible)
        self.update.connect('changed', self.update_list)
        self.config.connect('changed', self.load_config)

        self.add(self.wrapper)
        self.wrapper.pack_start(self.search_entry, False, False, 0)
        # self.wrapper.pack_start(self.scrollbox, True, True, 0)
        self.scrollbox.add(self.scrollframe)
        self.scrollframe.add(self.box)
        self.box.add(self.app_menu)
        
        self.app_list = []

        self.load_config(None, None, None, Gio.FileMonitorEvent.CHANGES_DONE_HINT)
        self.con_search()
        self.load_apps()
        # self.assemble()
        self.configure()
        #self.clear()

    def load_config(self, m, f, o, event):
        if event == Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            buffer = open(conf_file, "r")
            for line in buffer:
                if line.startswith('CommandSearch'):
                    self.cmdsearch = str2bool(line.rstrip().split('=')[1])
                if line.startswith('Math'):
                    self.math = str2bool(line.rstrip().split('=')[1])
                elif line.startswith('WebSearch'):
                    self.websearch = str2bool(line.rstrip().split('=')[1])
                elif line.startswith('Notify'):
                    self.notify = str2bool(line.rstrip().split('=')[1])
                elif line.startswith('RunCmd'):
                    self.runcmd = str2bool(line.rstrip().split('=')[1])

    def con_search(self):
        #self.search_entry.set_placeholder_text('Enter program name')
        self.search_entry.set_icon_from_icon_name(0, 'search')
        self.search_entry.set_icon_tooltip_text(1, 'Search for Applications')
        self.search_entry.connect('changed', self.search)
        self.search_entry.connect('activate', self.launch)
        BigFont = Pango.FontDescription("Sans Regular 14")
        self.search_entry.modify_font(BigFont)

    def update_list(self, m, f, o, event):
        if event == Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            self.app_list = []

            self.load_apps()
            self.clear()
            self.assemble()

    def load_apps(self):
        app_count = 0

        for file in os.listdir(applications):
            if os.path.isfile(os.path.join(applications, file)):
                buffer = open(applications + '/' + file, "r")

                name = "void"
                icon = "void"
                desc = "void"
                cmd = "void"

                for line in buffer:
                    if line.startswith("Icon="):
                        icon = line[5:].rstrip()
                    if line.startswith("Name="):
                        name = line[5:].rstrip()
                    if line.startswith("Comment="):
                        desc = line[8:].rstrip()
                    if line.startswith("Exec="):
                        cmd = line[5:].rstrip().lower()
                        cmd = cmd.replace("%u","")
                        cmd = cmd.replace("%f","")

                    if icon is not "void" and name is not "void" and cmd is not "void" and desc is not "void":
                        btn_app = appbutton()
                        btn_app.construct(icon, name, desc, cmd)

                        self.app_list.append(btn_app)
                        app_count += 1

                        icon = "void"
                        name = "void"
                        desc = "void"
                        cmd = "void"

    def configure(self):
        self.set_decorated(False)
        self.resize(400,28)
        #menu.set_size_request(350,5)
        #menu.move(0,0)
        self.set_skip_pager_hint(True)
        self.set_skip_taskbar_hint(True)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

    def clear(self):
        for widget in self.app_menu:
            self.app_menu.remove(widget)

    def found_in(self, query, item):
        if (self.cmdsearch):
            if query in str(self.app_list[item].get_info()).lower():
                return True
        else:
            if query in str(self.app_list[item].get_basic_info()).lower():
                return True
        return False

    def populate(self):
        apps = 0
        query = self.search_entry.get_text()
        if query != "":
            for item in range(0, len(self.app_list)):
                if self.found_in(query.lower(), item):
                    self.app_menu.pack_start(self.app_list[item].get_button(), True, True, 0)
                    apps += 1
                    self.found = True
                    
        if apps < 5 and apps > 0:
            for item in range(0, 5 - apps):
                space = spacer()
                self.app_menu.pack_start(space.get_box(), True, True, 0)
        elif apps == 0:
            label = Gtk.Label('No apps found')
            label.set_hexpand(True)
            label.set_alignment(0.5,0)
            if len(self.app_list) == 0:
                self.found = False
            self.app_menu.pack_end(label, True, True, 5)

    def launch(self, *data):
        if (self.found):
            child = self.app_menu.get_children()
            child[0].grab_focus()
            self.activate_focus()
        else:
            self.invisible(None, None)

    def search(self, entry):
        if entry.get_text() != "":
            if self.no_search == True:
                self.no_search = False
                self.wrapper.pack_start(self.scrollbox, True, True, 0)
            self.found = False
            self.clear()
            self.resize(400, 170)
            self.activate(entry.get_text())
            self.populate()
            self.show_all()
        else:
            self.wrapper.remove(self.scrollbox)
            self.no_search = True
            self.found = False
            self.configure()

    def assemble(self):
        for item in range(0, len(self.app_list)):
            self.app_menu.add(self.app_list[item].get_button())

    def invisible(self, object, event):
        self.hide()
        self.visible = False
        self.search_entry.set_text('')
        self.no_search = True
        self.wrapper.remove(self.scrollbox)
        self.resize(400, 28)

    def toggle_visible(self, m, f, o, event):
        if event == Gio.FileMonitorEvent.CHANGES_DONE_HINT:
            if self.visible:
                self.invisible(None, None)
            else:
                self.visible = True
                self.show_all()
                self.set_focus()
        
    def set_focus(self):
        self.present()
        self.set_modal(True)
        self.set_keep_above(True)

    def on_key_press(self, widget, event):
        key = Gdk.keyval_name(event.keyval)
        if 'Escape' in key:
            print(str(key))
            self.invisible(None, None)

    def render_result(self, text, icon, cmd):
        result = appbutton()
        result.construct(text, text, icon, cmd)
        result.set_label(str(text))
        result.set_font("Sans Regular", 14)
        result.set_icon(icon, Gtk.IconSize.MENU)
        
        self.app_menu.add(result.get_button())

    #### Extensions ####
    def activate(self, input):
        if (self.math):
            import extensions.umath.math
            math_module = extensions.umath.math
            
            operation = math_module.main(input)
            if operation != 0:
                self.render_result(str(operation[0]), operation[1], operation[2])
                self.found = True
                return operation

        if (self.websearch):
            import extensions.websearch.search
            web_module = extensions.websearch.search
            
            operation = web_module.main(input)
            if operation != 0:
                self.render_result(operation[0], operation[1], operation[2])
                self.found = True
                
        if (self.notify):
            import extensions.notify.notify
            notif_module = extensions.notify.notify
            
            operation = notif_module.main(input)
            if operation != 0:
                self.render_result(operation[0], operation[1], operation[2])
                self.found = True
                
        if (self.runcmd):
            import extensions.run.runcmd
            runcmd_module = extensions.run.runcmd
            
            operation = runcmd_module.main(input)
            if operation != 0:
                self.render_result(operation[0], operation[1], operation[2])
                self.found = True

app = launcher()
app.invisible(None, None)
Gtk.main()
