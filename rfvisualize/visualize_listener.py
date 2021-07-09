import os
import platform
import glob
import time
from robot.running.builder.parsers import RobotParser
from robot.running import EXECUTION_CONTEXTS
from robot.libraries.BuiltIn import BuiltIn

from fixture_parser import fixture
from gui_runner import gui_runner
from node import node
from node import rf
from win_renderer import win_renderer
from SeleniumLibrary import ElementFinder

# Time of render the element which current manipulating
render_delay = .261

# Keywords which should be ignored from rendering
ignore_render_keyword_list = []

# Keywords which don't need to be parse
bypass_build_keyword_list = []

class visualize_listener:
    ROBOT_LISTENER_API_VERSION = 2

    def __init__(self):
        self.init_block()
        self.runner = gui_runner()
        self.platform = platform.system()

        self.execution_flow = []
        self.is_suite_teardown = False
        self.in_suite_teardown = False
        self.finder = ElementFinder.find
        self.is_render_on = False

        self.runner.run()
        while not self.runner.is_runner_ready:
            pass

        for i in range(len(ignore_render_keyword_list)):
            ignore_render_keyword_list[i] = ignore_render_keyword_list[i].lower()

    def start_suite(self, name, attr):
        self.current_file_path = attr['source']
        if os.path.isdir(attr['source']):
            self.block_folder_initer()
        elif os.path.isfile(attr['source']):
            self.block_suite()
        else:
            raise Exception("Fail to switch source.")

    def start_test(self, name, attr):
        self.testcase_name = attr['originalname']
        self.block_test()

    def start_keyword(self, name, attr):
        if fixture(attr['kwname'], []).is_fixture:
            return
        if EXECUTION_CONTEXTS.current.in_suite_teardown:
            if not self.in_suite_teardown:
                self.in_suite_teardown = True
                if not self.is_suite_teardown:
                    self.runner.set_window_title("Suite Teardown")
                    self.runner.set_node_list(self.suite_teardown.pop())
                else:
                    self.runner.set_window_title("Suite Teardown (__init__)")
                    self.runner.set_node_list(self.folder_initer_teardown.pop())
        self.execution_flow.append(attr['kwname'])
        if len(self.execution_flow) == 1:
            if self.runner.is_start_node:
                self.runner.is_start_node = False
            else:
                self.runner.next_node()
        else:
            self.runner.next_keyword(attr['kwname'], attr['args'])
        self.test_block()

        if self.runner.is_render_ready:
            if attr['kwname'].lower() in ignore_render_keyword_list:
                self.is_render_on = False
                ElementFinder.find = self.finder
            elif not self.is_render_on:
                self.is_render_on = True
                self.render()
        else:
            if self.is_render_on:
                self.is_render_on = False
                ElementFinder.find = self.finder

    def end_keyword(self, name, attr):
        if fixture(attr['kwname'], []).is_fixture:
            return
        if attr['status'] == "FAIL":
            self.runner.on_fail()
        elif attr['status'] == "PASS":
            self.runner.on_pass()
        self.execution_flow.pop(-1)

    def end_suite(self, name, attr):
        self.in_suite_teardown = False
        if not self.is_suite_teardown:
            self.is_suite_teardown = True
        else:
            if not self.folder_initer_teardown:
                self.runner.on_closing()

    def init_block(self):
        self.folder_initer_setup = []
        self.folder_initer_teardown = []
        self.suite_setup = []
        self.suite_teardown = []
        self.test_setup = []
        self.test_script = []
        self.test_teardown = []

    def block_folder_initer(self):
        self.runner.set_window_title("Suite Setup (__init__)")
        self.blocker(self.folder_initer_setup, self.folder_initer_teardown, isdir=True)

    def block_suite(self):
        self.runner.set_window_title("Suite Setup")
        self.blocker(self.suite_setup, self.suite_teardown, isdir=False)

    def block_test(self):
        self.runner.set_window_title("Test: {}".format(self.testcase_name))
        self.blocker(self.test_setup, self.test_teardown, isdir=False, script=self.test_script)

    def blocker(self, setup, teardown, isdir, script=None):
        if script is not None:
            def parse(keyword, resource, instance):
                node_list = []
                if fixture(keyword.name, []).is_fixture:
                    kw_list, args_list = fixture(keyword.name, keyword.args).parse()
                    for kw, args in zip(kw_list, args_list):
                        node_list.append( node(kw, self.current_file_path, resource, args, keyword.type) )
                else:
                    node_list.append( node(keyword.name, self.current_file_path, resource, keyword.args, keyword.type) )
                for n in node_list:
                    n.build(bypass_build_keyword_list)
                instance.extend(node_list)

            self.test_setup.clear()
            self.test_teardown.clear()
            self.test_script.clear()
            rf.clear()
            suite = RobotParser().parse_suite_file(source=self.current_file_path)

            resource = []
            for imp in suite.resource.imports:
                if imp.type == "Resource":
                    if os.path.isfile(os.path.join(os.path.dirname(suite.resource.source), imp.name)):
                        resource.append(os.path.normpath(os.path.join(os.path.dirname(suite.resource.source), imp.name)))
                    elif os.path.isfile(BuiltIn().replace_variables(imp.name)):
                        resource.append(BuiltIn().replace_variables(imp.name))

            for test in suite.tests:
                if test.name == self.testcase_name:
                    for keyword in test.keywords:
                        if keyword.type == "setup":
                            parse(keyword, resource, self.test_setup)
                        elif keyword.type == "teardown":
                            parse(keyword, resource, self.test_teardown)
                        else:
                            if keyword.type == "for":
                                for for_item in keyword.keywords:
                                    parse(for_item, resource, self.test_script)
                            else:
                                parse(keyword, resource, self.test_script)
            self.runner.set_node_list(self.test_setup + self.test_script + self.test_teardown)
        else:
            def parse(source, setup, teardown):
                suite = RobotParser().parse_suite_file(source=source)

                resource = []
                for imp in suite.resource.imports:
                    if imp.type == "Resource":
                        if os.path.isfile(os.path.join(os.path.dirname(suite.resource.source), imp.name)):
                            resource.append(os.path.normpath(os.path.join(os.path.dirname(suite.resource.source), imp.name)))
                        elif os.path.isfile(BuiltIn().replace_variables(imp.name)):
                            resource.append(BuiltIn().replace_variables(imp.name))

                for keyword in suite.keywords:
                    node_list = []
                    if fixture(keyword.name, keyword.args).is_fixture:
                        kw_list, args_list = fixture(keyword.name, keyword.args).parse()
                        for kw, args in zip(kw_list, args_list):
                            node_list.append( node(kw, source, resource, args, keyword.type) )
                    else:
                        node_list.append( node(keyword.name, source, resource, keyword.args, keyword.type) )

                    for n in node_list:
                        n.build(bypass_build_keyword_list)
                    if keyword.type == "setup":
                        setup.extend(node_list)
                    elif keyword.type == "teardown":
                        teardown.append(node_list)
                    else:
                        raise Exception("Parse suite fail.")

            self.folder_initer_setup.clear()
            rf.clear()
            if isdir:
                if os.path.exists(self.current_file_path + "/__init__.robot"):
                    parse(self.current_file_path + "/__init__.robot", self.folder_initer_setup, self.folder_initer_teardown)
                    self.runner.set_node_list(self.folder_initer_setup)
            else:
                parse(self.current_file_path, self.suite_setup, self.suite_teardown)
                self.runner.set_node_list(self.suite_setup)

    def test_block(self):
        if self.runner.is_pause_ready:
            self.runner.can_step = True
        while self.runner.is_pause_ready:
            pass
        if self.runner.is_script_select or self.runner.is_keyword_tree_select:
            self.runner.clear_selection()

    def render(self):
        def wrapping(func):
            def do(element, panel_height):
                if self.platform == 'Windows':
                    rdr = win_renderer(element.location['x'], element.location['y'] + panel_height)
                    rdr.render(element.size['width'], element.size['height'])
                    start = time.time()
                    while time.time() - start < render_delay:
                        rdr.render(element.size['width'], element.size['height'])
                    win_renderer(-1, -1).stop_render()

            def wrapper(*args, **kwargs):
                rs = func(*args, **kwargs)
                lib = BuiltIn().get_library_instance('SeleniumLibrary')
                panel_height = lib.driver.execute_script('return window.outerHeight - window.innerHeight;')
                if rs:
                    if type(rs) == list:
                        for r in rs:
                            do(r, panel_height)
                    else:
                        do(rs, panel_height)
                return rs
            return wrapper
        ElementFinder.find = wrapping(ElementFinder.find)