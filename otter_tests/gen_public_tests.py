import os, nbformat, nbconvert, copy, shutil, json, ast, sys, subprocess, datetime
from nbformat.v4 import new_code_cell, new_markdown_cell, new_raw_cell, new_notebook


def get_sys_path():
    '''this helper function gets the path of the directory which contains the `otter_tests` directory'''
    for path in sys.path:
        otter_path = os.path.join(path, "otter_tests")
        if os.path.exists(otter_path):
            return otter_path


def read_nb(file):
    '''read notebook file'''
    with open(file, encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)
    return nb


def public_tests_parse_check(text):
    '''parse some code `text` and identify all calls to `public_tests.check` or `grader.check`'''
    t = ast.parse(text)
    for node in ast.walk(t):
        if not isinstance(node, ast.Call):
            continue
        if not 'value' in node.func._fields:
            continue
        if ast.unparse(node.func.value) in ['public_tests', 'grader'] and node.func.attr == 'check':
            return node.args[0].value


def public_tests_detect_namedtuple(text):
    '''parse some code `text` and identify all initializations of namedtuples'''
    for node in ast.walk(ast.parse(text)):
        if not isinstance(node, ast.Call):
            continue
        if 'namedtuple' in ast.unparse(node.func).split(".")[:2]:
            return node.args[0].value


def public_tests_bad_calls_check(text):
    '''identify calls to functions such as `grader.export`, `public_tests.rubric_check`, etc.,
    that need to be ignored while running the notebook to generate the `public_tests.py` file'''
    for node in ast.walk(ast.parse(text)):
        if not isinstance(node, ast.Call):
            continue
        if not 'value' in node.func._fields:
            continue
        if ast.unparse(node.func.value) in ['public_tests', 'grader', 'public_tests.hidn'] and node.func.attr != 'check':
            return True
    return False


def write_public_tests_check(text, answers, namedtuples_already_found):
    '''replace the `grader.check` (or `public_tests.check`) calls with code to update global variables
    that will store the values of all the correct answers; the name of the global variable that needs
    to be updated, as well as the variable that stores the answer are obtained from `answers`; also
    identify all namedtuple initializations and store their definitions in a global variable; finally
    delete all calls to bad functions'''
    if public_tests_bad_calls_check(text):
        return ""
    
    namedtuple_found = public_tests_detect_namedtuple(text)
    if namedtuple_found != None and namedtuple_found not in namedtuples_already_found:
        text += "\nexpected_namedtuples += '''\\n%s'''\n" % (ast.unparse(ast.parse(text)))
        text = "expected_namedtuples += '\\nglobal %s'\n" % (namedtuple_found) + text
        text += "expected_namedtuples += '\\nexpected_namedtuples.append(%s)'\n" % (namedtuple_found)
        namedtuples_already_found.append(namedtuple_found)

    qnum_check = public_tests_parse_check(text)
    if qnum_check == None or qnum_check not in answers:
        return text
        
    answer = answers[qnum_check]
    if answer['format'] == "TEXT_FORMAT_SPECIAL_ORDERED_LIST":
        output_text = 'special_json["%s"] = copy.deepcopy(%s)' % (qnum_check, answer['answer'])
    elif answer['format'] == "PNG_FORMAT_SCATTER":
        output_text = 'expected_plots["%s"] = copy.deepcopy(%s)' % (qnum_check, answer['answer'])
    elif answer['format'] in ["HTML_FORMAT_ORDERED", "HTML_FORMAT_UNORDERED"]:
        output_text = "table = bs4.BeautifulSoup(%s, 'html.parser')\n" % (answer['answer'])
        output_text += 'table.find("table")["data-question"] = "%s"\n' % (qnum_check)
        output_text += 'expected_dfs.append("<h1>Data Frame %s</h1>")\n' % (qnum_check)
        output_text += 'expected_dfs.append(table)'
    else:
        output_text = 'expected_json["%s"] = copy.deepcopy(%s)' % (qnum_check, answer['answer'])
    handler_node = ast.ExceptHandler()
    handler_node.body = [ast.Pass()]
    try_node = ast.Try()
    try_node.body = [ast.parse(output_text)]
    try_node.handlers = [handler_node]
    try_node.orelse, try_node.finalbody = [], []
    return ast.unparse(try_node)


class RemoveBadImports(ast.NodeTransformer):
    '''remove all imports to `public_tests`'''
    def generic_visit(self, node):
        super().generic_visit(node)
        return node

    def visit_Import(self, node):
        new_names = []
        for name in node.names:
            if name.name != 'public_tests':
                new_names.append(name)
        node.names = new_names
        if node.names == []:
            return ast.Pass()
        return node


'''code that needs to be injected to the notebook to initialize the global variables
and then after they are updated, use them to write `public_tests.py`'''
code_injections = {}

code_injections["public_tests_initializations"] = """
import ast, pprint, json, os, copy, bs4, re

expected_json = {}
special_json = {}
expected_plots = {}
expected_dfs = bs4.BeautifulSoup('', 'html.parser')
expected_namedtuples = 'expected_namedtuples = []\\n'

f = open('answers.json', encoding='utf-8')
expected_format = json.load(f)
f.close()
for key in expected_format:
    expected_format[key] = expected_format[key]["format"]"""

code_injections["public_tests_read"] = """
def get_json(text, target):
    t = ast.parse(text)
    for node in ast.walk(t):
        if type(node) == ast.FunctionDef and node.name == 'get_' + target:
            for item in node.body:
                if type(item) == ast.Assign and item.targets[0].id == target:
                    return ast.unparse(item)

def process_types_separately(text):
    for type_class_obj in re.findall("<class '[^>]*'>", text):
        text = text.replace(type_class_obj, type_class_obj[8:-2])
    return text

public_tests = {}"""

code_injections["public_tests_write"] = """
new_format = pprint.pformat(expected_format, sort_dicts=False).replace("\\n", "\\n" + " "*22)
public_tests = public_tests.replace(get_json(public_tests, 'expected_format'), 'expected_format = ' + new_format)
public_tests = process_types_separately(public_tests)

new_expected = pprint.pformat(expected_json, sort_dicts=False).replace("\\n", "\\n" + " "*20)
public_tests = public_tests.replace(get_json(public_tests, 'expected_json'), 'expected_json = ' + new_expected)
public_tests = process_types_separately(public_tests)

new_special = pprint.pformat(special_json, sort_dicts=False).replace("\\n", "\\n" + " "*19)
public_tests = public_tests.replace(get_json(public_tests, 'special_json'), 'special_json = ' + new_special)
public_tests = process_types_separately(public_tests)

expected_namedtuples = expected_namedtuples.replace("\\n", "\\n" + " " * 4)
public_tests = public_tests.replace(get_json(public_tests, 'expected_namedtuples'), expected_namedtuples)

f = open('public_tests.py', 'w', encoding='utf-8')
f.write(public_tests)
f.close()

if expected_plots != {}:
    f = open('expected_plots.json', 'w', encoding='utf-8')
    json.dump(expected_plots, f)
    f.close()

formatter = bs4.formatter.HTMLFormatter(indent=4)
if len(expected_dfs) != 0:
    f = open('expected_dfs.html', 'w', encoding='utf-8')
    f.write(expected_dfs.prettify(formatter=formatter))
    f.close()"""

code_injections["total_score_adjustment_p1"] = """
public_tests = public_tests.replace('TOTAL_SCORE = 100', 'TOTAL_SCORE = 25')
f = open('public_tests.py', 'w', encoding='utf-8')
f.write(public_tests)
f.close()"""

code_injections["total_score_adjustment_p9"] = """
public_tests = public_tests.replace('TOTAL_SCORE = 100', 'TOTAL_SCORE = 50')
f = open('public_tests.py', 'w', encoding='utf-8')
f.write(public_tests)
f.close()"""


def get_public_tests_nb(nb, answers):
    '''inject code to the notebook defining the global variables, replace all calls to
    `grader.check` (or `public_tests.check`) with code that updates the global variables
    with the answers, remove all import calls to `public_tests`, remove all bad
    function calls, and at the end, inject code that  writes the values of these variables
    into `public_tests.py`'''
    sys_path = get_sys_path()
    f = open(os.path.join(sys_path, 'templates', 'public_tests_template.py'), encoding='utf-8')
    public_tests = f.read()
    f.close()

    new_cells = []
    without_bad_imports = RemoveBadImports()
    new_cells.append(new_code_cell(code_injections['public_tests_initializations']))
    namedtuples_already_found = []
    for cell in nb['cells']:
        if cell['cell_type'] != 'code':
            continue
        try:
            cell['source'] = ast.unparse(without_bad_imports.visit(ast.parse(cell['source'])))
            public_check = write_public_tests_check(cell['source'], answers, namedtuples_already_found)
            new_cells.append(new_code_cell(public_check))
        except SyntaxError:
            cell['source'] = ""
    new_cells.append(new_code_cell(code_injections['public_tests_read'].format(repr(public_tests))))
    new_cells.append(new_code_cell(code_injections['public_tests_write']))
    nb['cells'] = new_cells
    return nb


def run_public_tests_nb(nb, gen_public_tests_file):
    '''run the modified notebook that generates `public_tests.py`'''
    with open(gen_public_tests_file, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
    with open(gen_public_tests_file, encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)
    ep = nbconvert.preprocessors.ExecutePreprocessor(timeout=300, kernel_name='python3')
    out = ep.preprocess(nb, {'metadata': {'path': os.path.dirname(gen_public_tests_file)}})


def gen_public_tests(FILE, keep_tests_file=False):
    '''reads the given `file` and `answers.json` and uses them to generate `gen_public_tests.ipynb`,
    then executes the notebook to generate `public_tests.py`'''
    nb = read_nb(FILE)
    directory = os.path.dirname(FILE)
    curr_time = str(datetime.datetime.now()).replace(":", "-").replace(" ", "-").split(".")[0]
    gen_public_tests_file = os.path.join(directory, "gen_public_tests-%s.ipynb" % (curr_time))

    f = open(os.path.join(directory, 'answers.json'), encoding='utf-8')
    answers = json.load(f)
    f.close()
    
    tests_nb = get_public_tests_nb(nb, answers)
    if os.path.basename(FILE) == 'p1.ipynb':
        tests_nb['cells'].append(new_code_cell(code_injections['total_score_adjustment_p1']))
    elif os.path.basename(FILE) == 'p9.ipynb':
        tests_nb['cells'].append(new_code_cell(code_injections['total_score_adjustment_p9']))
    run_public_tests_nb(tests_nb, gen_public_tests_file)
    
    if not keep_tests_file:
        os.remove(gen_public_tests_file)
