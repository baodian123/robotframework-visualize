class fixture:

    _fixture = [ 'run keywords' ]

    def __init__(self, name, args):
        self.is_fixture = bool(name.lower() in self._fixture)
        self.args = list(args)
        self.name = name

    def parse(self):
        def run_keywords_parser(args):
            kw_list, arg_list, temp_list = [], [], []
            flag = True
            for arg in args:
                if flag:
                    kw_list.append(arg)
                    flag = False
                elif arg.lower() == 'and':
                    arg_list.append(temp_list.copy())
                    temp_list.clear()
                    flag = True
                else:
                    temp_list.append(arg)
            arg_list.append(temp_list.copy())
            return (kw_list, arg_list)

        if not self.is_fixture:
            return [ self.name ], self.args

        if self.name.lower() == 'run keywords':
            kw_lst, arg_lst = run_keywords_parser(self.args)
            return (kw_lst, arg_lst)

        raise Exception("Fixture keyword parsing error.")

if __name__ == "__main__":
    is_fixture = fixture('Run keywords', ['Log', 'A', 'AND', 'Log Source', 'AND', 'Log', 'B'])
    n_fixture = fixture('run keyword', ['A', 'B', 'C'])
    assert is_fixture.is_fixture == True
    assert n_fixture.is_fixture == False
    kw_list, arg_list = is_fixture.parse()
    assert kw_list == ['Log', 'Log Source', 'Log']
    assert arg_list == [['A'], [], ['B']]
    n_kw_list, n_arg_list = n_fixture.parse()
    assert n_kw_list == ['run keyword']
    assert n_arg_list == ['A', 'B', 'C']