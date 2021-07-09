import threading
import tkinter as tk
from tkinter import ttk
from node import node

class gui_runner(object):

    GENERAL_MODE = "GENERAL_MODE"
    DETAILED_MODE = "DETAILED_MODE"

    COVER = '#53FF53'
    GREEN = '#53FF53'
    RED = '#FF5151'

    def __init__(self):
        self.node = []
        self.mode = self.GENERAL_MODE
        self.is_runner_ready = False
        self.is_pause_ready = False
        self.is_script_select = False
        self.is_keyword_tree_select = False
        self.is_render_ready = False
        self.can_step = False
        self.block_next_keyword = False
        self.block_next_node = False

    def run(self):
        self.thread = threading.Thread(target=self.show)
        self.thread.start()

    def show(self):
        self.set_window_configuration()
        self.make_vision()
        self.window.mainloop()

    def set_window_configuration(self):
        self.window = tk.Tk()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.window.title("Runner")
        self.window.resizable(True, True)
        self.window.attributes("-alpha", 0.8)
        self.window.attributes("-topmost", True)

    def set_window_title(self, title):
        self.window.title(title)

    def on_closing(self):
        self.is_pause_ready = False
        self.window.quit()

    def make_vision(self):
        def make_steps_vision(window):
            self.script = tk.Listbox(window, width='50', height='7', selectmode=tk.MULTIPLE, font=('Comic Sans MS', 12), exportselection=0)
            self.script.grid(row=1, columnspan=3, sticky="nsew")

        def make_keyword_tree_vision(window):
            self.keyword_tree = tk.Listbox(window, width='50', height='7', selectmode=tk.MULTIPLE, font=('Comic Sans MS', 12), exportselection=0)
            self.keyword_tree.grid(row=2, columnspan=3, sticky="nsew")

            if self.node:
                self.keyword_tree.insert('end', self.node[self.current_node_index].payload)
                self.insert_tree_vision(self.node[self.current_node_index], self.keyword_tree)

        def make_function(window):
            self.function_resume = tk.Button(window, text='Resume', command=self.function_resume_callback)
            self.function_pause = tk.Button(window, text='Pause', command=self.function_pause_callback)
            self.function_step_into = tk.Button(window, text='Step Into', command=self.step_into_callback)
            self.function_step_over = tk.Button(window, text='Step Over', command=self.step_over_callback)
            self.render_text = tk.StringVar()
            self.render_text.set("Render / Off")
            self.render = tk.Button(window, textvariable=self.render_text, command=self.render_callback)
            self.transparency_scale = ttk.Scale(window, from_=25, to=100, orient='horizontal', command=self.update_transparency)

            self.function_resume.grid(row=3, column=0, sticky="nsew")
            self.function_pause.grid(row=4, column=0, sticky="nsew")
            self.function_step_into.grid(row=3, column=1, sticky="nsew")
            self.function_step_over.grid(row=4, column=1, sticky="nsew")
            self.render.grid(row=3, column=2, sticky="nsew")
            self.transparency_scale.grid(row=4, column=2, sticky="nsew")
            self.transparency_scale.set(80)

        def set_grid_config():
            self.window.grid_columnconfigure(0, weight=1)
            self.window.grid_rowconfigure(1, weight=1)
            self.window.grid_columnconfigure(1, weight=1)
            self.window.grid_columnconfigure(2, weight=1)

        def switch_vision():
            if self.radio.get() == 0:
                self.keyword_tree.grid_forget()
                self.window.grid_rowconfigure(2, weight=0)
                self.mode = self.GENERAL_MODE
            elif self.radio.get() == 1:
                self.window.grid_rowconfigure(2, weight=1)
                make_keyword_tree_vision(self.window)
                self.mode = self.DETAILED_MODE
                self.keyword_tree.itemconfig(self.keyword_tree_index, bg=self.COVER)
                self.keyword_tree.see(self.keyword_tree_index)

        self.radio = tk.IntVar()
        tk.Radiobutton(self.window, text="General", variable=self.radio, value=0, command=switch_vision).grid(row=0, column=0, columnspan=2)
        tk.Radiobutton(self.window, text="Detailed", variable=self.radio, value=1, command=switch_vision).grid(row=0, column=1, columnspan=2)

        make_steps_vision(self.window)
        make_function(self.window)
        set_grid_config()
        if self.mode == self.DETAILED_MODE:
            self.radio.set(1)
            make_keyword_tree_vision(self.window)
        
        self.is_runner_ready = True

    def set_node_list(self, node):
        self._disabled_button(self.function_resume, self.function_pause, self.function_step_into, self.function_step_over)

        self.is_start_node = True
        self.node = node
        self.current_node_index, self.keyword_tree_index = 0, 0
        self.script.delete(0, 'end')

        for n in self.node:
            if n.keyword_type == "setup":
                self.script.insert('end', " + " + n.payload)
            elif n.keyword_type == "teardown":
                self.script.insert('end', " - " + n.payload)
            else:
                self.script.insert('end', n.payload)

        if self.node:
            self.script.itemconfig(self.current_node_index, bg=self.COVER)

            self._pause_ready()
            self.is_pause_ready = True

        if self.mode == self.DETAILED_MODE:
            if self.node:
                self.set_start_keyword_tree_vision()

    def set_start_keyword_tree_vision(self):
        self.keyword_tree.delete(0, 'end')
        self.keyword_tree.insert('end', self.node[self.current_node_index].payload)
        self.insert_tree_vision(self.node[self.current_node_index], self.keyword_tree)
        self.keyword_tree.itemconfig(0, bg=self.COVER)

    def next_node(self):
        self.current_node_index += 1
        self.keyword_tree_index = 0

        if self.current_node_index > 0:
            self.script.itemconfig(self.current_node_index-1, bg='')
        self.script.itemconfig(self.current_node_index, bg=self.COVER)
        self.script.see(self.current_node_index)

        if self.mode == self.DETAILED_MODE:
            self.set_start_keyword_tree_vision()

        if self.is_select(self.script, self.current_node_index):
            self.is_script_select = True

        if self.block_next_node:
            self.block_next_node = False
            self._pause_ready()
            self.is_pause_ready = True

    def next_keyword(self, name, args):
        def is_next(node, name, args):
            if node:
                return node.name == name and node.args == list(args)
            return False
        if not is_next(self.node[self.current_node_index].get_node_by_id(self.keyword_tree_index+1), name, args):
            return
        self.keyword_tree_index += 1
        if self.mode == self.DETAILED_MODE:
            if self.keyword_tree_index > 0:
                self.keyword_tree.itemconfig(self.keyword_tree_index-1, bg='')
            self.keyword_tree.itemconfig(self.keyword_tree_index, bg=self.COVER)
            self.keyword_tree.see(self.keyword_tree_index)
            if self.is_select(self.keyword_tree, self.keyword_tree_index):
                self.is_keyword_tree_select = True
            if self.block_next_keyword:
                self.block_next_keyword = False
                self._pause_ready()
                self.is_pause_ready = True

    def is_select(self, listbox, index):
        if index in listbox.curselection():
            self._pause_ready()
            self.is_pause_ready = True
            return True
        return False

    def clear_selection(self):
        if self.is_script_select:
            self.script.selection_clear(0, self.current_node_index)
        elif self.is_keyword_tree_select:
            if self.mode == self.DETAILED_MODE:
                self.keyword_tree.selection_clear(0, self.keyword_tree_index)

    def insert_tree_vision(self, node, vision, indentation=" |  "):
        for child in node.children:
            vision.insert('end', indentation + child.payload)
            if len(child.children):
                self.insert_tree_vision(child, vision, indentation + " |  ")

    def function_pause_callback(self):
        self._pause_ready()
        self.is_pause_ready = True

    def function_resume_callback(self):
        self._pause_prepare()
        self.is_pause_ready = False

    def step_into_callback(self):
        if self.can_step and self.mode == self.DETAILED_MODE:
            self._pause_prepare()
            self.is_pause_ready = False
            self.block_next_keyword = True

    def step_over_callback(self):
        if self.can_step:
            self._pause_prepare()
            self.is_pause_ready = False
            self.block_next_node = True

    def render_callback(self):
        if not self.is_render_ready:
            self.is_render_ready = True
            self.render_text.set("Render / On")
        else:
            self.is_render_ready = False
            self.render_text.set("Render / Off")

    def update_transparency(self, event):
        self.window.attributes("-alpha", (float)(self.transparency_scale.get())/100.0)

    def _enabled_button(self, *buttons):
        for button in buttons:
            button['state'] = tk.NORMAL

    def _disabled_button(self, *buttons):
        for button in buttons:
            button['state'] = tk.DISABLED

    def _pause_ready(self):
        self._disabled_button(self.function_pause)
        self._enabled_button(self.function_resume, self.function_step_into, self.function_step_over)

    def _pause_prepare(self):
        self._enabled_button(self.function_pause)
        self._disabled_button(self.function_resume, self.function_step_into, self.function_step_over)

    def on_fail(self):
        self.COVER = self.RED
        self.cover()

    def on_pass(self):
        self.COVER = self.GREEN
        self.cover()

    def cover(self):
        self.script.itemconfig(self.current_node_index, bg=self.COVER)
        if self.mode == self.DETAILED_MODE:
            self.keyword_tree.itemconfig(self.keyword_tree_index, bg=self.COVER)

if __name__ == "__main__":
    gui_runner = gui_runner()
    n1 = node( "keyword A", "", [], ['a1', 'a2'], "" )
    n2 = node( "keyword B", "", [], ['b1', 'b2'], "" )
    n3 = node( "keyword C", "", [], ['c1', 'c2'], "" )

    node_list = [n1, n2, n3]
    gui_runner.run()
    while not gui_runner.is_runner_ready:
        pass
    gui_runner.set_node_list(node_list)