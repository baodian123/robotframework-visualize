from robot.running.builder.parsers import RobotParser
from robot.libraries.BuiltIn import BuiltIn
import os

# refactor: pack this variable into 'node', or we need to clear when block changed.
rf = {}

class node:
    def __init__(self, name, file_path, resources, args, keyword_type):
        self.name = name
        self.file_path = file_path
        self.resources = resources.copy()
        self.args = list(args)
        self.keyword_type = keyword_type
        self.children = []
        self.id = -1

        self.payload = name
        if self.args:
            self.payload += " : " + "  ".join(self.args)

        self.tree = [ self.payload ]
        self._format_path(self.resources)

    def build(self, bypass_build_keyword_list=[]):
        self.build_keyword_tree_from_test_file(bypass_build_keyword_list)
        self.build_keyword_tree_from_resource_file(bypass_build_keyword_list)
        self.recursion_append_keyword_tree()
        self.add_node_id(0)

    def build_keyword_tree_from_test_file(self, bypass_build_keyword_list=[]):
        if self.name in bypass_build_keyword_list:
            return
        robot_file = RobotParser().parse_suite_file(source=self.file_path)
        for local_keyword in robot_file.resource.keywords:
            if local_keyword.name.lower() == self.name.lower():
                for step in local_keyword.keywords:
                    if step.type == "for":
                        for for_item in step.keywords:
                            self.children.append( node(for_item.name, self.file_path, self.resources, for_item.args, for_item.type) )
                    else:
                        self.children.append( node(step.name, self.file_path, self.resources, step.args, step.type) )
                break
        for child in self.children:
            child.build_keyword_tree_from_test_file(bypass_build_keyword_list)
        if not rf:
            imports = []
            for resource in self.resources:
                imports.extend(self._get_all_imports(RobotParser().parse_resource_file(resource)))
            self.resources.extend(imports)
            self.resources = list(set(self.resources))
            for resource in self.resources:
                rf[resource] = RobotParser().parse_resource_file(resource)
        else:
            self.resources = list(rf.keys())

    def build_keyword_tree_from_resource_file(self, bypass_build_keyword_list=[]):
        if self.name in bypass_build_keyword_list:
            return
        if self.children:
            for child in self.children:
                child.build_keyword_tree_from_resource_file(bypass_build_keyword_list)
            return

        flag = False
        for resource in self.resources:
            resource_file = rf[resource]
            for resource_keyword in resource_file.keywords:
                if resource_keyword.name.lower() == self.name.lower():
                    for step in resource_keyword.keywords:
                        if step.type == "for":
                            for for_item in step.keywords:
                                self.children.append( node(for_item.name, resource_file.source, self._get_all_imports_from_rf_file(resource), for_item.args, for_item.type) )
                        else:
                            self.children.append( node(step.name, resource_file.source, self._get_all_imports_from_rf_file(resource), step.args, step.type) )
                    flag = True
                    break
            if flag:
                break

        for child in self.children:
            child.build_keyword_tree_from_resource_file(bypass_build_keyword_list)
        if not self.children:
            bypass_build_keyword_list.append(self.name)

    def _get_all_imports(self, resource_file):
        imports = [ resource_file.source ]
        for imp in resource_file.imports:
            if imp.type == "Resource":
                if os.path.isfile(os.path.join(os.path.dirname(resource_file.source), imp.name)):
                    imports.extend(self._get_all_imports(RobotParser().parse_resource_file(os.path.normpath(os.path.join(os.path.dirname(resource_file.source), imp.name)))))
                elif os.path.isfile(BuiltIn().replace_variables(imp.name)):
                    imports.extend(self._get_all_imports(RobotParser().parse_resource_file(BuiltIn().replace_variables(imp.name))))

        self._format_path(imports)
        return list(set(imports))

    def _get_all_imports_from_rf_file(self, resource):
        resource = resource.replace('\\', '/').replace('\\\\', '/')
        imports = [ resource ]
        for imp in rf[resource].imports:
            if imp.type == "Resource":
                if os.path.isfile(os.path.join(os.path.dirname(rf[resource].source), imp.name)):
                    imports.extend(self._get_all_imports_from_rf_file(os.path.normpath(os.path.join(os.path.dirname(rf[resource].source), imp.name))))
                elif os.path.isfile(BuiltIn().replace_variables(imp.name)):
                    imports.extend(self._get_all_imports_from_rf_file(BuiltIn().replace_variables(imp.name)))
        
        return list(set(imports))

    def _format_path(self, resources):
        for i in range(len(resources)):
            resources[i] = resources[i].replace('\\', '/').replace('\\\\', '/')

    def add_node_id(self, id):
        self.id = id
        for child in self.children:
            id = child.add_node_id(id + 1)
        return id

    def get_node_by_id(self, id):
        if self.id == id:
            return self
        if not self.children:
            return None
        for child in self.children:
            node = child.get_node_by_id(id)
            if node:
                return node
        return None

    def recursion_print_node_id(self):
        for child in self.children:
            print(child.id, end='')
            if len(child.children):
                child.recursion_print_node_id()

    def print_keyword_tree(self):
        print(self.name, end='')
        if self.args:
            print(" : " + '  '.join(self.args))
        else:
            print()
        self.recursion_print_node(self)

    def recursion_print_node(self, node):
        for child in node.children:
            print(child.name, end='')
            if child.args:
                print(" : " + '  '.join(child.args))
            else:
                print()
            if len(child.children):
                self.recursion_print_node(child)

    def recursion_append_keyword_tree(self):
        for child in self.children:
            if child.children:
                child.recursion_append_keyword_tree()
            for n in child.tree:
                self.tree.append(n)

if __name__ == "__main__":
    from io import StringIO
    import sys

    n = node("Logoff ezScrum", os.path.abspath("Test ezScrum/ezScrum project panel should contain at least one project.robot"), ["keywords/common.txt"], [], " ")
    n.build_keyword_tree_from_test_file()
    n.build_keyword_tree_from_resource_file()

    print_keyword_tree_output = StringIO()
    sys.stdout = print_keyword_tree_output
    n.print_keyword_tree()
    sys.stdout = sys.__stdout__

    recursion_tree_output = StringIO()
    sys.stdout = recursion_tree_output
    n.recursion_append_keyword_tree()
    for k in n.tree:
        print(k)
    sys.stdout = sys.__stdout__

    assert print_keyword_tree_output.getvalue() == recursion_tree_output.getvalue()

    n.add_node_id(n.id)

    print_id_output = StringIO()
    sys.stdout = print_id_output
    n.recursion_print_node_id()
    sys.stdout = sys.__stdout__

    for index, id in enumerate(print_id_output.getvalue()):
        assert int(id) == index

    assert n.get_node_by_id(-1) == n
    assert n.get_node_by_id(4) == None