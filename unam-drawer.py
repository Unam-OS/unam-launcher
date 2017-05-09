#!/usr/bin/python3

import gi
import os
import re
import threading
import subprocess
import setproctitle

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk

setproctitle.setproctitle('unam-menu')

def log(message):
    home = os.getenv("HOME")
    file = home + "/.config/unam/unam-menu/logs/log"

    with open(file, "a") as logfile:
        logfile.write(message + '\n')

def getScreenSize():
    output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True,stdout=subprocess.PIPE).communicate()[0]
    output = output.rstrip()
    output = str(output)
    
    # remove unnecessary characters
    output = output[2:]
    output = output[:-1]
    return output

def getPanelSize():
    home = os.getenv("HOME")
    path = home + '/.config/tint2'
    file = 'tint2rc'
    if os.path.isfile(os.path.join(path, file)):
        buffer = open(path + '/' + file, "r")
        
        for line in buffer:
            if 'panel_size' in line:
                height = line.rstrip()
                height = height.split()
        return height[3]

class unam_menu(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Unam Menu")

        self.icon = Gtk.Image()
        self.icon.set_from_icon_name('app-launcher', Gtk.IconSize.DIALOG)
        self.render_icon('app-launcher', Gtk.IconSize.MENU)

        self.connect("delete-event", self.quit)
        self.connect('focus-out-event', self.quit)
        self.connect('key_press_event', self.on_key_press)

        self.semaphore = threading.Semaphore(4)
        self.wrapper = Gtk.VBox()
        self.scrollbox = Gtk.ScrolledWindow()
        self.scrollframe = Gtk.Viewport()
        self.box = Gtk.Box(spacing=6)   
        self.spacer_left = Gtk.Box()
        self.spacer_right = Gtk.Box()
        self.controlbox = Gtk.HBox(spacing=2)
        self.searchbox = Gtk.Box(spacing=20)
        self.app_grid = Gtk.Grid()
        self.search_entry = Gtk.Entry()

        self.add(self.wrapper)
        self.controlbox.pack_start(self.spacer_left, True, True, 0)
        self.controlbox.pack_start(self.search_entry, True, True, 0)
        self.controlbox.pack_start(self.spacer_right, True, True, 0)
        self.wrapper.pack_start(self.controlbox, False, False, 0)
        self.wrapper.pack_start(self.scrollbox, True, True, 0)
        self.scrollbox.add(self.scrollframe)
        self.scrollframe.add(self.box)
        self.box.add(self.app_grid)
        
        self.spacer_right.set_halign(Gtk.Align.END)
        self.search_entry.set_icon_from_icon_name(1, 'search')
        self.search_entry.set_icon_tooltip_text(1, 'Search for Applications')
        self.search_entry.connect('changed', self.search)

        self.btn_list = []
        self.labels = []

        self.add_items()
        self.build_menu()
        
    def add_items(self):

        path = '/usr/share/applications'
        app_id = 0

        for file in os.listdir(path):
            # print(file)

            if os.path.isfile(os.path.join(path, file)):

                buffer = open(path + '/' + file, "r")
                # print(buffer.read())

                icon = "void"
                name = "void"
                desc = "void"
                cmd = "void"

                for line in buffer:
                    if line.startswith("Icon="):
                        icon = line
                        icon = icon[5:]
                        icon = icon.rstrip()
                    if line.startswith("Name="):
                        name = line
                        name = name[5:]
                        name = name.rstrip()
                    if line.startswith("Comment="):
                        desc = line
                        desc = desc[8:]
                        desc = desc.rstrip()
                    if line.startswith("Exec="):
                        cmd = line
                        cmd = cmd[5:]
                        cmd = cmd.rstrip()

                    if icon is not "void" and name is not "void" and cmd is not "void" and desc is not "void":

                        self.image = Gtk.Image()
                        self.image.set_from_icon_name(icon, Gtk.IconSize.DIALOG)

                        self.btn_list.append(Gtk.Button())
                        self.labels.append(Gtk.Label(name, 12))
                        
                        self.layoutbox = Gtk.VBox()
                        self.layoutbox.add(self.image)
                        self.layoutbox.add(self.labels[app_id])

                        classes = self.btn_list[app_id].get_style_context()
                        classes.add_class('flat')

                        self.btn_list[app_id].add(self.layoutbox)
                        self.btn_list[app_id].set_hexpand(True)
                        self.btn_list[app_id].set_tooltip_text(desc)
                        self.btn_list[app_id].connect("clicked" , self.button_click, cmd)

                        app_id += 1

                        icon = "void"
                        name = "void"
                        desc = "void"
                        cmd = "void"

        log("Apps loaded")

    def button_click(self, button, *data):
        command = str(data)
        command = command[2:]
        command = command[:-3]

        # Start process with new thread
        with self.semaphore:
                os.system(command + '&')
                log("App launched: " + command)

                self.quit()

    def build_menu(self):

        column = 1
        row = 1
        items = len(self.btn_list)
        for item in range(0, items):
                self.app_grid.attach(self.btn_list[item], column, row, 1, 1)
                if column == 3:
                        column = 0
                        row += 1
                column += 1
        log('Added items to menu')

    def clear(self):
        items = len(self.btn_list)
        for item in range(0, items):
                self.app_grid.remove(self.btn_list[item])

    def sort(self):
        column = 1
        row = 1
        items = len(self.btn_list)
        
        for item in range(0, items):
            if self.search_entry.get_text().lower() in self.labels[item].get_text().lower():
                self.app_grid.attach(self.btn_list[item], column, row, 1, 1)
                if column == 3:
                        column = 0
                        row += 1
                column += 1
        
    def search(self, entry):
        self.clear()
        self.sort()

    def on_key_press(self, widget, event):
        key = Gdk.keyval_name(event.keyval)
        print(key)
        if 'Escape' in key:
            self.quit()

    def quit(self, event, *data):
        running = os.getenv("HOME") + "/.config/unam/unam-menu/running"
        os.system("truncate -s 0 " + running + " &")
        
        Gtk.main_quit()

position = getScreenSize()
position = position.split('x')

y = int(position[1]) - int(getPanelSize()) - 600

menu = unam_menu()
menu.set_decorated(True)

menu.set_skip_taskbar_hint(True)
menu.set_skip_pager_hint(True)

menu.resize(660,600)
menu.set_position(Gtk.WindowPosition.CENTER_ALWAYS) # launcher mode
# menu.move(0, y)

menu.show_all()

menu.present()
menu.set_modal(True)
menu.set_keep_above(True)
Gtk.main()
