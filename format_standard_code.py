import sys
import typing
import inspect
from pprint import pformat
from collections import defaultdict
from dev.lib.utils_ import *

py38 = not sys.version_info >= (3, 9)


def format_module(module_docKKN):
    module = []
    for func, func_docKN in module_docKKN.items():
        source = inspect.getsourcelines(func)[0]
        indent = get_indent(source[0])
        if type(func).__name__ in {"function", "method"}:
            heading = '\n'.join([
                "",
                format_def(func_docKN),
                f'""" {func.__doc__ or ""}',
                format_example(func_docKN),
                f'"""',
            ]).replace('\n', '\n' + indent // 4 * '\t')
            content = ''.join(line for line in source if get_indent(line) > indent)
            module += [heading + '\n' + content]
        else:
            raise NotImplementedError
    return '\n'.join(module)

def format_example(func_docKN):
    doc = []
    for example in func_docKN.example:
        input = pformat(example.input).replace('\n', '\n\t\t')
        output = pformat(example.output).replace('\n', '\n\t\t')
        doc += [f"\tinput:\n\t\t{input}\n\toutput:\n\t\t{output}"]
    return '\n'.join(doc).replace("Ellipsis", "...")

def format_def(func_docKN):
    public_name = func_docKN.public_name
    exampleN = func_docKN.example
    if len(exampleN) == 1:
        inputK, output = exampleN[0].input, exampleN[0].output
        func = [
            f"def {public_name}(", [
                f"\t{k}: {typing_of(v, outmost=True)},"
                for k, v in inputK.items()
            ],
            f"): -> {typing_of(output, outmost=True)}"
        ]
    else:
        merged_inputK = defaultdict(list)
        merged_output = []
        for example in exampleN:
            for k, v in example.input.items():
                merged_inputK[k] += [v]
                merged_output += [example.output]
        func = [
            f"def {public_name}(", [
                f"\t{k}: {union_of(v, outmost=True)},"
                for k, v in merged_inputK.items()
            ],
            f"): -> {union_of(merged_output, outmost=True)}"
        ]
    func = '\n'.join(flatten(func)).replace('typing.', '')
    return func

def union_of(itemN, outmost=False):
    typ = {}
    for item in itemN:
        typ[typing_of(item)] = None # ordered set
    if len(typ) == 1 and outmost:
        return typing_of(itemN[0], outmost=True)
    return typing.Union.__getitem__(tuple(typ.keys()))

def typing_of(obj, outmost=False):
    if isinstance(obj, dict):
        key_type = union_of(obj.keys())
        value_type = union_of(obj.values())
        return (typing.Dict if py38 else dict)[key_type, value_type]
    elif isinstance(obj, list):
        item_type = union_of(obj)
        return (typing.List if py38 else list)[item_type]
    elif isinstance(obj, tuple):
        item_type = [typing_of(item) for item in obj]
        return (typing.Tuple if py38 else tuple)[tuple(item_type)]
    elif obj == ...:
        return typing.Any
    else:
        return type(obj).__name__ if outmost else type(obj)

if __name__ == '__main__':
    class A:
        def a():
            pass

        def b():
            pass

    doc_structKKN = {
        A.a: dotdict(
            public_name="abc",
            example=[
                dotdict(
                    input={"x": 2, "y": "3"},
                    output=[1, 2],
                ),
                dotdict(
                    input={"x": ...},
                    output='2',
                ),
            ]
        ),
        A.b: dotdict(
            public_name="ghi",
            example=[],
        )
    }
    print(format_module(doc_structKKN))
