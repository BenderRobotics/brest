from brest.gui.controllers import ResourceController, ConfigController

import tkinter as tk
from tkinter import Menu


def dummy_command():
    print("meh just a dummy, what a bummer")


def main():
    # * Create main window
    root = tk.Tk()
    root.title("Brest")
    root.geometry("400x400")

    # * Create menu
    menubar = Menu(root)

    # * Create menu fields
    filemenu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=filemenu)

    # * Add menubar
    root.config(menu=menubar)

    # * Insert panned window to split in half
    p_window = tk.PanedWindow(root, orient=tk.HORIZONTAL)
    p_window.pack(fill="both", expand=True)

    # * Create controllers
    resource_controller = ResourceController(p_window)
    # config_controller = ConfigController(p_window)

    # * Add views to panned window
    p_window.add(resource_controller.resource_view.frame)
    # p_window.add(config_controller.view)

    # * Fill menu fields
    # filemenu.add_command(label="New Config", command=config_controller.add_tab)
    # filemenu.add_command(label="Open Config", command=config_controller.add_tab)
    # filemenu.add_command(label="Close Config", command=config_controller.view.close_selected_tab)
    # filemenu.add_command(label="Save Config", command=dummy_command)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)

    # config_controller.open_user_config()
    root.mainloop()


if __name__ == '__main__':
    main()
