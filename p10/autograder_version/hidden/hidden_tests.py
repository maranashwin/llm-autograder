import copy, os, math, ast, re, json, random, time
import nbformat, nbconvert
from nbformat.v4 import new_code_cell
from collections import namedtuple
import datetime
from pymongo import MongoClient, ReturnDocument

DIRECTORY = '.'
TESTS_FILE = os.path.join('hidden', 'hidden_tests.ipynb')
PASS = "All test cases passed!"
hidden_tests_executables = None
results = {}

NECESSARY_FILES = ['public_tests.py', 'data', 'README.md', 'rubric.md', 'images']
FILE = 'p10.ipynb'
TOTAL_SCORE = 100

URI = 'mongodb+srv://uwcs220:ZvKIsNACl2LLwkpm@cluster0.fr7f8yc.mongodb.net/?retryWrites=true&w=majority'
DB_NAME = "students"
COLLECTION_NAME = "ld"

def read_nb(file):
    '''read_nb(file) reads a file in the `.ipynb` file format'''
    with open(file, encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)
    return nb

def run_nb(nb, file):
    '''run_nb(nb, file) executes `nb` at the location `file` and writes the contents back into `file`'''
    with open(file, "w", encoding='utf-8') as f:
        nbformat.write(nb, f)
    with open(file, encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)

    ep = nbconvert.preprocessors.ExecutePreprocessor(timeout=300, kernel_name='python3')
    out = ep.preprocess(nb, {'metadata': {'path': os.path.dirname(file)}})
    with open(file, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
    return nb

def parse_nb(nb):
    '''parse_nb(nb) read the contents of a student `nb` and extracts all graded questions and answers'''
    questions = {}
    for cell in nb['cells']:
        if cell['cell_type'] == 'code' and 'grader.check' in cell['source']:
            qnum = cell['source'].split('grader.check(')[1].split(')')[0][1:-1]
            output = []
            if 'outputs' not in cell:
                continue
            for output_cell in cell['outputs']:
                if 'text' in output_cell:
                    output.extend(output_cell["text"].split("\n"))
                elif 'data' in output_cell and 'text/plain' in output_cell['data']:
                    output.extend(output_cell["data"]["text/plain"].split("\n"))
            for line in output:
                if line.split(":")[0] != qnum + " results":
                    continue
                questions[qnum] = ":".join(line.split(":")[1:]).strip()
    return questions

def detect_syntax_error(text):
    '''detect_syntax_error(text) interprets `text` as Python code and flags if it contains any Syntax Errors'''
    try:
        ast.parse(text)
        compile(text, filename='<string>', mode='exec')
    except Exception as e:
        return type(e).__name__ + ": " + str(e)
    return False

def standardize_code(text):
    '''standardize_code(text) removes all comments, removes line breaks in code, standardizes use of
    horizontal and vertical whitespace, and the use of quotation marks around strings'''
    return ast.unparse(ast.parse(text))

class RemovePrints(ast.NodeTransformer):
    '''child class of the ast.NodeTransformer class, used for removing print statements from code'''

    def generic_visit(self, node):
        '''helper function used for traversing the Abstract Syntax Tree'''
        super().generic_visit(node)
        return node

    def visit_Call(self, node):
        '''visit_Call(self, node) replaces all print statements traversed with a tuple that contains the contents
        of the print statement'''
        if 'id' in node.func._fields and node.func.id == 'print':
            new_node = ast.Tuple()
            new_node.elts = node.args
            return new_node
        else:
            return node

def remove_prints(text):
    '''remove_prints(text) uses an object of the RemovePrints class to remove all print statements from code'''
    without_prints = RemovePrints()
    return ast.unparse(without_prints.visit(ast.parse(text)).body)

class ReplaceSlashes(ast.NodeTransformer):
    '''child class of the ast.NodeTransformer class, used for replacing forward slashes in strings with backslashes'''

    def generic_visit(self, node):
        '''helper function used for traversing the Abstract Syntax Tree'''
        super().generic_visit(node)
        return node

    def visit_Constant(self, node):
        '''visit_Constant(self, node) replaces all instances of forward slashes in strings with backslashes'''
        if isinstance(node.value, str):
            node.value = node.value.replace('\\', '/')
        return node

def replace_slashes_text(text):
    '''replace_slashes_text(text) replaces all instances of double forward slashes that appear within strings in `text`
    with backslashes'''
    replace_slashes = ReplaceSlashes()
    return ast.unparse(replace_slashes.visit(ast.parse(text)).body)

def replace_slashes(nb, start=None, end=None):
    '''replace_slashes(nb) replaces all instances of double forward slashes that appear within strings in code cells
    of `nb` with backslashes between indices `start` and `end`'''
    if start == None:
        start = 0
    if end == None:
        end = len(nb['cells'])
    for idx in range(start, end):
        if nb['cells'][idx]['cell_type'] != "code":
            continue
        nb['cells'][idx]['source'] = replace_slashes_text(nb['cells'][idx]['source'])
    return nb

class RemovePublicTests(ast.NodeTransformer):
    '''child class of the ast.NodeTransformer class, used for removing all bad references to the module `public_tests`'''

    def generic_visit(self, node):
        '''helper function used for traversing the Abstract Syntax Tree'''
        super().generic_visit(node)
        return node

    def visit_Name(self, node):
        '''visit_Name(self, node) replaces all instances of `public_tests` with some junk'''
        if node.id == "public_tests":
            node.id = "cheater"
        return node
    
    def visit_Import(self, node):
        '''visit_Import(self, node) replaces all instances of a different module being imported
        as `public_tests` with some junk'''
        for idx in range(len(node.names)):
            if node.names[idx].asname == "public_tests":
                node.names[idx].asname = "cheater"
            elif node.names[idx].name == "public_tests" and node.names[idx].asname != None:
                node.names[idx].name = "cheater"
        return node
    
    def visit_Constant(self, node):
        '''visit_Constant(self, node) replaces all instances of `public_tests` with some junk'''
        if isinstance(node.value, str):
            node.value = node.value.replace("public_tests", "cheater")
        return node

def remove_public_tests_text(text):
    '''remove_public_tests_text(text) removes all unexpected references to `public_tests` in the notebook'''
    remove_public_tests = RemovePublicTests()
    return ast.unparse(remove_public_tests.visit(ast.parse(text)).body)

def add_try_except(text):
    '''add_try_except(text) adds a (bare) try/except block around any given block of code'''
    except_handler = ast.ExceptHandler()
    except_handler.body = [ast.Pass()]
    try_block = ast.Try()
    try_block.body = ast.parse(text).body
    try_block.handlers = [except_handler]
    try_block.orelse = []
    try_block.finalbody = []
    return ast.unparse(try_block)

def truncate_nb(nb, start=None, end=None):
    '''truncate_nb(nb, start, end) takes in a `nb`, and returns a sliced notebook between the cells indexed 
    `start` and `end`'''
    nb = copy.deepcopy(nb)
    if start == None:
        start = 0
    if end == None:
        end = len(nb['cells']) - 1
    nb['cells'] = nb['cells'][start: end+1]
    return nb

def clean_nb(nb):
    '''clean_nb(nb) takes in a `nb` and returns a cleaned `nb` after removing cells with Syntax Errors, removing
    all print statements, replacing all forward slashes in strings with backslashes (to make paths Linux-consistent),
    and adding try/except around all cells, standatdizing the text, and removing the export call'''
    global syntax_error_cells
    nb = truncate_nb(nb, end=find_all_cell_indices(nb, "markdown", "## Submission")[-1])

    syntax_error_cells = {}
    error_free_cells = []
    for cell in nb['cells']:
        if cell['cell_type'] != "code":
            error_free_cells.append(cell)
            continue
        syntax_error = detect_syntax_error(cell['source'])
        if syntax_error != False:
            error_msg = syntax_error[:-1] + ", cell %s)" % (str(cell['execution_count']))
            syntax_error_cells[error_msg] = cell['source']
        else:
            cell['source'] = remove_public_tests_text(remove_prints(standardize_code(cell['source'])))
            if cell['source'] != '' and not detect_func_calls_text(cell['source'], ['grader']):
                cell['source'] = add_try_except(cell['source'])
            error_free_cells.append(cell)
    nb['cells'] = error_free_cells
    return nb

def detect_public_tests():
    '''detect_public_tests() returns `True` if there are any references to `public_tests` in `FILE`
    other than the `import public_tests`'''
    bad_public_tests = 0
    if FILE not in os.listdir(DIRECTORY):
        return False
    nb = read_nb(os.path.join(DIRECTORY, FILE))
    for cell in nb['cells']:
        if cell['cell_type'] != "code":
            continue
        if 'public_tests' not in cell['source']:
            continue
        if cell['source'] in ['import public_tests', 'public_tests.reset_hidden_tests()']:
            continue
        bad_public_tests += 1
    
    if bad_public_tests > 0:
        return True
    return False

def detect_restart_and_run_all(nb):
    '''detect_restart_and_run_all(nb) flags if any non-empty code cell in `nb` is not executed'''
    for cell in nb['cells']:
        if cell['cell_type'] == "code" and cell["source"] != "":
            if cell['execution_count'] == None:
                return False
    return True

def detect_imports(nb):
    '''detect_imports(nb) returns a list of all the import statements in the `nb`'''
    imports = []
    for cell in nb['cells']:
        if cell['cell_type'] != "code":
            continue
        for node in ast.walk(ast.parse(cell['source'])):
            if isinstance(node, ast.Import):
                for import_statement in node.names:
                    imports.append(import_statement.name)
            elif isinstance(node, ast.ImportFrom):
                for import_statement in node.names:
                    imports.append(node.module + "." + import_statement.name)
    return imports

def detect_ast_objects_text(text, objects):
    '''detect_ast_objects_text(text, objects) returns any ast objects `objects` are found in the text'''
    found_objects = []
    for node in ast.walk(ast.parse(text)):
        for object in objects:
            if isinstance(node, object):
                found_objects.append(object)
    return found_objects

def detect_ast_objects(nb, objects):
    '''detect_ast_objects(nb, objects) returns a dict of all cells in the `nb` with the ast objects `objects` in them'''
    found_cells = {}
    for cell in nb['cells']:
        if cell['cell_type'] == "code":
            found_objects = detect_ast_objects_text(cell['source'], objects)
            if found_objects == []:
                continue
            if cell['execution_count'] not in found_cells:
                found_cells[str(cell['execution_count'])] = ([], cell['source'])
            found_cells[str(cell['execution_count'])][0].extend(found_objects)
    return found_cells

def unpack_func_call_node(node):
    '''unpack_func_call_node(node) is a helper function that takes in a function call node and returns all attributes
    in the function call'''
    if isinstance(node, ast.Name):
        return [node.id]
    elif isinstance(node, ast.Attribute):
        return unpack_func_call_node(node.value) + [node.attr]
    elif isinstance(node, ast.Call):
        call_nodes = unpack_func_call_node(node.func)
        call_nodes[-1] = call_nodes[-1]+"()"
        return call_nodes
    else:
        return [ast.unparse(node)]

def detect_func_calls_text(text, func_attrs):
    '''detect_func_calls_text(text, func_attrs) returns any calls to any function with `func_attrs` found in the text'''
    func_calls = []
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.Call):
            found_func = unpack_func_call_node(node.func)
            is_func = True
            for idx in range(len(func_attrs)):
                if func_attrs[idx] != Ellipsis and idx < len(found_func) and func_attrs[idx] != found_func[idx]:
                    is_func = False
                    break
            if is_func:
                func_calls.append(".".join(found_func))
    return func_calls

def detect_func_calls(nb, func_attrs):
    '''detect_func_calls(nb, func_attrs) returns a dict of all cells in the `nb` with the calls
    to any function with `func_attrs` in them'''
    func_calls = {}
    for cell in nb['cells']:
        if cell['cell_type'] == "code":
            found_calls = detect_func_calls_text(cell['source'], func_attrs)
            if found_calls == []:
                continue
            if cell['execution_count'] not in func_calls:
                func_calls[str(cell['execution_count'])] = []
            func_calls[str(cell['execution_count'])].extend(found_calls)
    return func_calls

def detect_bare_excepts_text(text):
    '''detect_bare_excepts_text(text) flags if there is any bare except in the text'''
    for node in ast.walk(ast.parse(text)):
        if isinstance(node, ast.ExceptHandler) and node.type == None:
            return True
    return False

def detect_bare_excepts(nb):
    '''detect_bare_excepts(nb) returns a list of all the cells which contain bare try/except blocks'''
    bare_excepts = []
    for cell in nb['cells']:
        if cell['cell_type'] == "code" and detect_bare_excepts_text(cell['source']):
            if cell['execution_count'] not in bare_excepts:
                bare_excepts.append(str(cell['execution_count']))
    return bare_excepts

def find_cell_index(nb, cell_type, marker):
    '''find_cell_index(nb, cell_type, marker) returns the index of the first cell in `nb` of cell type `cell_type`
    that contains the `marker` in its source'''
    if cell_type == "code":
        marker = ast.unparse(ast.parse(marker))
    for idx in range(len(nb['cells'])):
        cell = nb['cells'][idx]
        if cell['cell_type'] == cell_type and marker in cell['source']:
            return idx
    return None

def find_all_cell_indices(nb, cell_type, marker):
    '''find_all_cell_indices(nb, cell_type, marker) returns all the indices in `nb` of cell type `cell_type`
    that contains the `marker` in its source'''
    indices = []
    nb = copy.deepcopy(nb)
    start_idx = 0
    while nb['cells'] != []:
        idx = find_cell_index(nb, cell_type, marker)
        if idx == None:
            break
        indices.append(start_idx + idx)
        nb = truncate_nb(nb, idx+1)
        start_idx += idx+1
    if indices == []:
        indices.append(None)
    return indices

def inject_code(nb, idx, code):
    '''inject_code(nb, idx, code) creates a new code cell in `nb` after the index `idx` with `code` in it'''
    nb['cells'].insert(idx, new_code_cell(code))
    return nb

def count_defns_node(node, func_name):
    '''count_defns_node(node, func_name) is a helper function that recursively counts the number of times `func_name`
    is defined in the `node`'''
    defns = 0
    for item in ast.walk(node):
        if isinstance(item, ast.FunctionDef) and item.name == func_name:
            dummy_fn = True
            for sub_item in item.body:
                if not isinstance(sub_item, ast.Pass):
                    dummy_fn = False
                    break
            if not dummy_fn:
                defns += 1
    return defns

def count_defns(nb, func_name):
    '''count_defns(nb, func_name) counts the number of times `func_name` is defined in the `nb`'''
    defns = 0
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            defns += count_defns_node(ast.parse(cell['source']), func_name)
    return defns

def replace_defn_node(node, func_name, new_defn):
    '''replace_defn_node(node, func_name, new_defn) is a helper function that replaces the definition of `func_name`
    in `node` with `new_defn`'''
    for i in range(len(node.body)):
        item = node.body[i]
        if isinstance(item, ast.FunctionDef) and item.name == func_name:
            node.body[i] = ast.parse(new_defn)
        elif 'body' in item._fields:
            node.body[i] = replace_defn_node(item, func_name, new_defn)
    return node

def replace_defn(nb, func_name, new_defn):
    '''replace_defn(nb, func_name, new_defn) replaces the definition of `func_name` in `nb` with `new_defn`'''
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            cell['source'] = ast.unparse(replace_defn_node(ast.parse(cell['source']), func_name, new_defn))
    return nb

class ReplaceFunction(ast.NodeTransformer):
    '''child class of the ast.NodeTransformer class, used for replacing one function with another'''
    
    def __init__(self, original_function, target_function):
        '''constructor for initializing the base class as well as the two function names'''
        super().__init__()
        self.original_function = original_function
        self.target_function = target_function
        
    def iterate_children(self, node):
        '''traverse over the children of the node'''
        children = ast.iter_child_nodes(node)
        for c in children:
            self.visit(c)

    def generic_visit(self, node):
        '''helper function used for traversing the Abstract Syntax Tree'''
        super().generic_visit(node)
        return node
    
    def visit_FunctionDef(self, node):
        '''visit_FunctionDef(self, node) replaces the defintion of the original function with the target function'''
        if node.name == self.original_function:
            node.name = self.target_function
        self.iterate_children(node)
        return node

    def visit_Call(self, node):
        '''visit_Call(self, node) replaces all calls to the original function with calls to the target function'''
        if isinstance(node.func, ast.Name) and node.func.id == self.original_function:
            node.func.id = self.target_function
        self.iterate_children(node)
        return node

def replace_call(text, func_name, new_name):
    '''replace_call(text, func_name, new_name) uses an object of the ReplaceFunction class to 
    replace all definitions and calls to `func_name` with `new_name` in `text`'''
    replace_calls_text = ReplaceFunction(func_name, new_name)
    return ast.unparse(replace_calls_text.visit(ast.parse(text)).body)

class ReplaceVariable(ast.NodeTransformer):
    '''child class of the ast.NodeTransformer class, used for replacing one variable with another'''
    
    def __init__(self, original_variable, target_variable):
        '''constructor for initializing the base class as well as the two variable names'''
        super().__init__()
        self.original_variable = original_variable
        self.target_variable = target_variable
        
    def iterate_children(self, node):
        '''traverse over the children of the node'''
        children = ast.iter_child_nodes(node)
        for c in children:
            self.visit(c)

    def generic_visit(self, node):
        '''helper function used for traversing the Abstract Syntax Tree'''
        super().generic_visit(node)
        return node

    def visit_Name(self, node):
        '''visit_Name(self, node) replaces all calls to the original variable with calls to the target variable'''
        if node.id == self.original_variable:
            node.id = self.target_variable
        return node

def replace_variable(text, variable_name, new_variable):
    '''replace_variable(text, variable_name, new_variable) uses an object of the ReplaceVariable class to 
    replace all instances of the variable `variable_name` with `new_variable` in `text`'''
    replace_variable_text = ReplaceVariable(variable_name, new_variable)
    return ast.unparse(replace_variable_text.visit(ast.parse(text)).body)

def parse_assign_targets_node(node):
    '''parse_assign_targets_node(node) identifies all the targets of an ast.Assign `node` and returns them as a list'''
    if isinstance(node, ast.Tuple):
        targets = []
        for subnode in node.elts:
            targets.extend(parse_assign_targets_node(subnode))
    elif isinstance(node, ast.Assign):
        targets = []
        for target in node.targets:
            targets.extend(parse_assign_targets_node(target))
    else:
        targets = [node]
    return targets    

def parse_assign_value_node(node):
    '''parse_assign_value_node(node) identifies all the values of an ast.Assign `node` and returns them as a list'''
    if isinstance(node, ast.Tuple):
        values = []
        for subnode in node.elts:
            values.extend(parse_assign_value_node(subnode))
    elif isinstance(node, ast.Assign):
        values = parse_assign_value_node(node.value)
    else:
        values = [node]
    return values    

class RemoveInitializations(ast.NodeTransformer):
    '''child class of the ast.NodeTransformer class, used for removing initializations of a particular variable from code'''
    
    def __init__(self, variable):
        '''constructor for initializing the base class as well as the variable name'''
        super().__init__()
        self.variable = variable

    def generic_visit(self, node):
        '''helper function used for traversing the Abstract Syntax Tree'''
        super().generic_visit(node)
        return node

    def visit_Assign(self, node):
        '''visit_Assign(self, node) replaces all assignments of `variable` with a statement that contains the contents
        of the value assigned to `variable'''
        targets = parse_assign_targets_node(node)
        values = parse_assign_value_node(node)
        variable_found = False
        for target in targets:
            if ast.unparse(target) == self.variable:
                variable_found = True
        if not variable_found:
            return node
        new_node = ast.Module()
        new_node.type_ignores = []
        new_node.body = []
        for idx in range(len(targets)):
            target = targets[idx]
            value = values[idx]
            if ast.unparse(target) != self.variable:
                new_assign = ast.Assign()
                new_assign.type_comment = None
                new_assign.targets = [target]
                new_assign.value = value
                new_assign.lineno = node.lineno + idx
                new_node.body.append(new_assign)
            else:
                new_expr = ast.Expr()
                new_expr.value = value
                new_node.body.append(new_expr)
        return new_node

def remove_initializations_text(text, variable):
    '''remove_initializations_text(text, variable) uses an object of the RemoveInitializations class to 
    remove all initializations of the variable `variable` in the `text`'''
    remove_initializations_text = RemoveInitializations(variable)
    return ast.unparse(remove_initializations_text.visit(ast.parse(text)).body)

def remove_initializations(nb, variable, start=None, end=None):
    '''remove_initializations(nb, variable, start, end) uses an object of the RemoveInitializations class to 
    remove all initializations of the variable `variable` in the `nb` between the indices `start` and `end`'''
    if start == None:
        start = 0
    if end == None:
        end = len(nb['cells'])-1
    for idx in range(start, end+1):
        cell = nb['cells'][idx]
        if cell['cell_type'] != "code":
            continue
        nb['cells'][idx]['source'] = remove_initializations_text(cell['source'], variable)
    return nb

def find_code(nb, target):
    '''find_code(nb, target) returns the number of times that `target` appears in a code cell in `nb`'''
    target_count = 0
    for cell in nb['cells']:
        if cell['cell_type'] != "code":
            continue
        target_count += cell['source'].count(target)
    return target_count

def replace_code(nb, target, new_code, start=None, end=None):
    '''replace_code(nb, target, new_code, start, end) replaces all instances of `target` in a code cell between
    the indices `start` and `end` with `new_code`'''   
    if start == None:
        start = 0
    if end == None:
        end = len(nb['cells']) - 1
        
    for idx in range(start, end+1):
        cell = nb['cells'][idx]
        if cell['cell_type'] != "code":
            continue
        nb['cells'][idx]['source'] = cell['source'].replace(target, new_code)
    return nb

def count_assignments(nb, variable):
    '''count_assignments(nb, variable) returns the number of times that `variable` is assigned a 
    value in a code cell of `nb`'''
    initializations = 0
    for cell in nb['cells']:
        if cell['cell_type'] != "code":
            continue
        for node in ast.walk(ast.parse(cell['source'])):
            if not isinstance(node, ast.Assign):
                continue
            targets = parse_assign_targets_node(node)
            for target in targets:
                if ast.unparse(target) == variable:
                    initializations += 1
    return initializations

def parse_rubric_file(rubric_file):
    '''reads `rubric_file` and returns a dict mapping each rubric point to the points allotted to it'''
    f = open(rubric_file, encoding='utf-8')
    all_data = f.read()
    f.close()

    rubric = {}

    data = all_data[all_data.lower().find('question specific guidelines'):]
    total_points = 0
    for line in data.split("\n")[1:]:
        line = line.replace("\t", "  ")
        if line.strip() == "":
            continue
        elif line.startswith("-"):
            if total_points > 0:
                rubric[directory + ": public tests"] = total_points
            directory = line.split("(")[0].strip(" -").replace("`", "")
            total_points = float(line.split("(")[1].split(")")[0].strip())
        elif line.startswith("  -"):
            subdirectory = line.split("(")[0].strip(" -")
            points = abs(float(line.split("(")[1].split(")")[0].strip()))
            rubric[directory + ": " + subdirectory] = points
            total_points -= points
            if points == total_points and 'hardcode' in subdirectory: # this is to ensure that in p2, hardcode tests don't mess with the points for the other rubric points
                continue
    if total_points > 0:
        rubric[directory + ": public tests"] = total_points

    general_deductions = all_data[all_data.lower().find('general guidelines'):all_data.lower().find('question specific guidelines')]
    for line in general_deductions.split("\n"):
        if line.strip() == "":
            continue
        elif line.startswith("-"):
            directory = line.split("(")[0].strip(" -")
            points = line.split("(")[1].split(")")[0].strip()
            if not points.replace("-", "").isnumeric():
                continue
            rubric["general_deductions: " + directory] = abs(int(points))

    return rubric

def get_directories(rubric, destination="."):
    '''get_directories(rubric, destination) takes in a `rubric` and returns a dict mapping each rubric point
    to the location within the `destination` of the directory associated with the rubric point'''
    directories = {}    
    subdirectories = {}
    
    for qnum in rubric:
        directory = qnum.split(':')[0]
        if directory not in subdirectories:
            subdirectories[directory] = 0
        rubric_item = ":".join(qnum.split(':')[1:]).strip()
        if directory == "general_deductions" or rubric_item == "public tests":
            continue
        subdirectories[directory] += 1
        directories[qnum] = os.path.join(destination, directory, str(subdirectories[directory]))
        
    return directories

def get_all_comments(directories):
    '''get_all_comments(directories) opens all the README files in `directories`, and extracts the comments under them'''
    comments = {}
    for qnum in directories:
        f = open(os.path.join(directories[qnum], 'README.txt'), encoding='utf-8')
        comments[qnum] = "\n".join(f.read().split("\n")[1:]).strip("\n ")
        f.close()
    return comments

def reset_hidden_tests():
    '''reset_hidden_tests() resets all the hidden test variables and clears the cache, 
    so that calls to `rubric_check` rerun all tests'''
    global hidden_tests_executables, results, deductions, comments
    hidden_tests_executables = None
    results = {}
    deductions = {}
    rubric = parse_rubric_file(os.path.join(DIRECTORY, "rubric.md"))
    directories = get_directories(rubric, "hidden")
    comments = get_all_comments(directories)

def get_hidden_tests_executables(tests_file=TESTS_FILE):
    '''get_hidden_tests_executables(tests_file) takes in the file with all the executable tests and updates a
    global dict to be a dict mapping each test to its code'''
    global hidden_tests_executables, results
    hidden_tests_executables = {}
    tests_nb = read_nb(tests_file)
    executable_tag = None
    
    for cell in tests_nb['cells']:
        if cell['cell_type'] == "raw" and '# BEGIN' in cell['source']:
            executable_tag = cell['source'].split('# BEGIN ')[1]
        elif executable_tag != None and cell['cell_type'] == "raw" and '# END ' +  executable_tag in cell['source']:
            executable_tag = None
        elif cell['cell_type'] == "code" and executable_tag != None:
            if executable_tag not in hidden_tests_executables:
                hidden_tests_executables[executable_tag] = ""
            hidden_tests_executables[executable_tag] += "\n" + cell['source']

def execute(tag, tests_file=TESTS_FILE):
    '''execute(tag, tests_file) executes the `tag` executable in `tests_file`'''
    global hidden_tests_executables, results
    if hidden_tests_executables == None:
        get_hidden_tests_executables(tests_file)
    just_questions = [result_tag.split(":")[0] for result_tag in results]
    if tag not in results and not (tag == 'hardcode' and tag in just_questions):
        code = ""
        initialize_tags = list(hidden_tests_executables.keys())
        initialize_tags = initialize_tags[:initialize_tags.index("original")]
        for initialize_tag in initialize_tags:
            code += hidden_tests_executables[initialize_tag] + "\n"
        code += hidden_tests_executables[tag]
        exec(code, globals())

def pre_check(qnum, tests_file=TESTS_FILE):
    '''pre_check(qnum, tests_file) executes and checks the pre-requisite tags in `tests_file` before
    any tag of `qnum` can be checked'''
    global hidden_tests_executables, results
    execute("original", tests_file)
    execute("hardcode", tests_file)
    
    if not (qnum.startswith("q") and qnum[1:].isnumeric()):
        return PASS
    if results['original'][qnum] != PASS:
        return "public tests failed"
    hardcode_test_pass = True
    for hardcode in results:
        if not hardcode.startswith("hardcode:"):
            continue
        hardcode_test_pass = False
        if results[hardcode][qnum] != PASS:
            hardcode_test_pass = True
            break
    if not hardcode_test_pass:
        return "answer is hardcoded"
    return PASS

def rubric_check(tag, files=NECESSARY_FILES, tests_file=TESTS_FILE):
    '''rubric_check(tag) performs some sanity checks and then executes the `tag` and outputs its result;
    if `only_tag` is set to False, then this check can fail only if all previous tests with the same qnum pass'''
    global results
    nb = clean_nb(read_nb(os.path.join(DIRECTORY, FILE)))
    if nb['cells'][0]['cell_type'] == "raw" and nb['cells'][0]['source'].startswith('# ASSIGNMENT CONFIG'):
        return PASS
    
    qnum = tag.split(":")[0]
    rubric_point = ":".join(tag.split(":")[1:]).strip(" ")
    
    pre_check_result = pre_check(qnum, tests_file)
    if pre_check_result != PASS:
        return pre_check_result
    
    if rubric_point == "public tests":
        return PASS
    
    execute(tag, tests_file)
        
    if results[tag][qnum] != PASS:
        return rubric_point
    else:
        return PASS

def make_deductions(rubric_item, tests_file=TESTS_FILE):
    '''make_deductions(rubric_item) updates the global variable `deductions` with the appropriate deduction
    for any `rubric_item`'''
    global rubric, deductions
    
    if rubric_item not in rubric:
        return
    try:
        qnum = rubric_item.split(":")[0].strip()
        pre_check_result = pre_check(qnum, tests_file)
    except:
        pre_check_result = 'hidden tests crashed before execution'
        
    if FILE not in os.listdir(DIRECTORY):
        deduction_item =  "file '%s' not found; make sure you have named your notebook as required\n" % (FILE)        
    elif pre_check_result == "public tests failed":
        deduction_item = '%s: public tests failed' % (qnum)
    elif pre_check_result == "answer is hardcoded":
        deduction_item = '%s: answer is hardcoded' % (qnum)
    elif pre_check_result == "hidden tests crashed before execution":
        deduction_item = '%s: hidden tests crashed before execution' % (qnum)
    else:
        deduction_item = rubric_item

    if deduction_item not in deductions:
        deductions[deduction_item] = 0
    deductions[deduction_item] += rubric[rubric_item]

def check_all_past_tags(tag, tests_file=TESTS_FILE):
    '''check_all_past_tags(tag) returns a list of all tags in the global variable `results` dependent on `tag`
    that failed their tests'''
    global results
    
    qnum = tag.split(":")[0].strip()
    relevant_qnums = [qnum] + re.findall('`(.*?)`', tag.split(":")[1].strip())
    
    failed_tags = []
    for past_tag in results:
        if past_tag == tag:
            continue
        past_qnum = past_tag.split(":")[0]
        if past_qnum not in relevant_qnums:
            continue
        if past_qnum not in results[past_tag]:
            continue
        if results[past_tag][past_qnum] != PASS:
            failed_tags.append(past_tag)
            
    if pre_check(qnum, tests_file) != PASS:
        failed_tags.append(qnum + ': public tests')
    return failed_tags

def get_comment(tag, tests_file=TESTS_FILE):
    '''get_comment(tag) returns the comment corresponding to a given `tag` as long as
    all other past tests dependent on `tag` passed their tests'''
    global comments
    
    qnum = tag.split(":")[0].strip()
    pre_check_result = pre_check(qnum, tests_file)
    if pre_check_result == "public tests failed":
        comment = "The public tests have failed, so you will not receive any points for this question."
        comment += "\nPlease confirm that the public tests pass locally before submitting."
        return comment
    elif pre_check_result == "answer is hardcoded":
        comment = "It is considered hardcoding to just store the correct value in the required variable"
        comment += "\nwithout using Python to compute the answer as required by this question."
        comment += "\nYou will not receive any points for this question."
        return comment
        
    past_failed_tags = check_all_past_tags(tag, tests_file)
    if qnum not in ["general_deductions"] and len(past_failed_tags) > 0:
        comment = "You are highly likely to have failed this test because of an error somewhere else"
        comment += "\nin your notebook. Take a look at the TEST DETAILS of the following test(s):"
        comment += "\n" + "\n".join(past_failed_tags)
        return comment
    if tag not in comments:
        return ""
    else:
        return comments[tag]

def get_directory_link(tag, tests_file=TESTS_FILE):
    '''get_directory_link(tag) returns link to the local directory which contains the test notebook for `tag`'''
    global directories
    
    qnum = tag.split(":")[0].strip()
    try:
        pre_check_result = pre_check(qnum, tests_file)
    except:
        pre_check_result = 'hidden tests crashed before execution'
    if pre_check_result == PASS and tag in directories:
        return directories[tag]
    return os.path.join("hidden", "original")

def get_num_late_days():
    '''
    Returns the datetime difference between the due
    date of the assignment and the time of the submission. 
    Return value is greater than or equal to 0 if on-time 
    or less than 0 if late. For example:
    
    if time_diff.total_seconds() >= 0:
        # Submission is on time, no deductions
    '''
    # ADDED: Spring break dates 2024
    excluded_dates = [
        (3, 23), (3,24), (3,25),
        (3,26), (3,27), (3,28),
        (3,29), (3,30), (3,31)
    ]
    try:
        with open("/autograder/submission_metadata.json") as f:
            obj = json.load(f)
            submission_time = obj["created_at"].split(".")[0]
            due_time = obj["assignment"]["due_date"].split(".")[0]
            submission_datetime = datetime.datetime.strptime(submission_time,"%Y-%m-%dT%H:%M:%S")
            due_datetime = datetime.datetime.strptime(due_time,"%Y-%m-%dT%H:%M:%S")
            days_late_delta = due_datetime - submission_datetime

            # ADDED:
            # Reduce number of days_late by the number of excluded
            # days that lie in-between when it was due and when
            # the student submitted the assignment
            for month, day in excluded_dates:
                excluded_date = datetime.datetime(due_datetime.year, month, day)
                if due_datetime <= excluded_date <= submission_datetime:
                    days_late_delta += datetime.timedelta(days=1)
                
            return days_late_delta
    except:
        return datetime.timedelta(0)

def get_student_emails():
    '''get_student_emails() returns a list of emails of the students listed in the submission's metadata.
    See https://gradescope-autograders.readthedocs.io/en/latest/submission_metadata/'''
    try:
        with open("/autograder/submission_metadata.json") as f:
            obj = json.load(f)
            return [dic["email"] for dic in obj["users"]]
    except:
        return ['amaran@wisc.edu']

def update_late_days(netid, proj_num, ld_used):
    """
    Creates a connection to the MongoDB cluster and updates
    the student's late days with a backoff strategy.
    With a maxPoolSize of 399, the maximum number of concurrent 
    connections that can be established to the MongoDB cluster 
    is limited to 399. This ensures that the number of connections
    does not exceed the limit of 500 and does not generate a warning
    (which occurs at 80% of max connections). This helps prevent connection 
    errors or performance degradation. When the function no longer
    needs the connection, it closes it, returning it to the pool.
    Short timeout (5 sec) helps reduce load on the cluster too.

    Parameters:
        netid (str): student whose late days should be updated
        proj_num (int): index of project to update, i.e. 3 for P3
        ld_used (int): number of late days used for project

    Returns:
        late_days (dict): late days dictionary where keys are project
                numbers as strings and values are late days used as ints
                (note that late days can be recorded past 12 total.)
                {
                    '3': 1,
                    '7': 3
                }
        None: if operation fails
    """
    
    max_attempts = 15
    filter_query = {"net_id": netid}
    update_query = {
        "$set": {f"late_days.{proj_num}": ld_used}
    }
    options = {
        "upsert": True,
        "return_document": ReturnDocument.AFTER
    }
    for _ in range(max_attempts):
        time.sleep(random.uniform(1, 7))
        try:
            client = MongoClient(
                URI,
                ssl=True,
                tls=True,
                tlsAllowInvalidCertificates=True,
                maxPoolSize=399,
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                serverSelectionTimeoutMS=5000,
            )
            collection = client[DB_NAME][COLLECTION_NAME]
            result = collection.find_one_and_update(
                filter_query,
                update_query,
                **options
            )
            return result.get("late_days") if result else None
        except Exception as e:
            print(e)
            if client:
                client.close()
            continue                
    print('Failed to connect to MongoDB Cluster and update late days.')
    return None

def per_student_ld_deduction(netid):
    """
    Given the netID of a student, return the 
    number of uncovered late days that student has used.
    
    Note that the entries in the late_days property
    of the documents in the ld collection in the 
    students database range from 0 to 3 but they can 
    total more than 12. For example, this is a valid 
    document for a student who used 3 late days
    for P2, P3, P4,and P5 and who just submitted
    P6 2 days late:
        {_id: 65ac76e188b4edf2556cb1de,
        net_id: "kgwilson2",
        late_days: {
            '2' : 3,
            '3' : 3,
            '4' : 3,
            '5' : 3,
            '6' : 2
        }
    In the above case, the 2 late days for P6 will be 
    recorded as 'used' in the database but we handle that 
    in this function so that they are uncovered late days
    that get deducted. 

    Parameters:
        netid (str): the netID of the student

    Returns:
        int: the number of uncovered late days used by the 
            student (0 if something went wrong)
    """
    project_name = FILE.split(".")[0].upper() # like "P2"
    project_num = int(project_name[1:]) # like 2
    
    # Calculate the time difference
    time_diff = get_num_late_days()
    
    # Check if  submission is on time (late submissions have negative time_diff)
    if time_diff.total_seconds() >= 0:
        # Submission is on time, no deductions
        return 0
    
    # If the project is late, update the student's late days
    days_late = math.ceil(-time_diff.total_seconds() / (24 * 3600)) 
    days_used = min(days_late, 3)

    # Update the ld collection on MongoDB
    updated_ld_dict = update_late_days(netid, project_num, days_used)
    if updated_ld_dict is None:
        return 0 # Something went wrong, don't make a deduction
    
    # If the student has used more than 12 late days total, 
    # that means the uncovered_ld needs to be increased.
    uncovered_ld = max(days_late - 3, 0)
    sum_ld_used = sum(updated_ld_dict.values())
    if sum_ld_used > 12:
        uncovered_ld += min(sum_ld_used - 12, days_used)

    return uncovered_ld

def update_late_day_deduction(total_score):
    """
    Calculates the late day deduction for each
    student based on the number of late days
    they used. 

    Parameters:
        total_score (int): Total score of the assignment

    Returns:
        (float): Late day deduction
    """
    # Get student info
    submission_emails = get_student_emails()
    student_netids = [email.split("@")[0].lower() for email in submission_emails]

    ld_deducs = []
    for netid in student_netids:
        uncovered_ld = per_student_ld_deduction(netid)
        ld_deducs.append(0.05 * total_score * uncovered_ld)
    
    if len(ld_deducs) > 0:
        return min(ld_deducs)
    else: 
        return 0 # Something went wrong, don't make a deduction

LATE_DAY_DEDUCTION_MADE = False
def make_late_day_deduction():
    '''make_late_day_deduction() updates the Late Days deduction sheet and makes the appropriate late day deduction
    to the project score'''
    global deductions, LATE_DAY_DEDUCTION_MADE
    if LATE_DAY_DEDUCTION_MADE:
        return
    LATE_DAY_DEDUCTION_MADE = True
    try:
        late_day_deduction = update_late_day_deduction(TOTAL_SCORE)
    except:
        late_day_deduction = 0
    if late_day_deduction > 0:
        deductions['Late Day deduction'] = late_day_deduction

def get_late_days_used():
    '''get_late_days_used() obtains details about the number of late days used by the student from the database'''
    net_id = get_student_emails()[0]
    max_attempts = 15
    client = None
    for _ in range(max_attempts):
        time.sleep(random.uniform(1, 7))
        # try:
        client = MongoClient(
            URI,
            ssl=True,
            tls=True,
            tlsAllowInvalidCertificates=True,
            maxPoolSize=399,
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            serverSelectionTimeoutMS=5000,
        )
        collection = client[DB_NAME][COLLECTION_NAME]
        student = collection.find_one({"net_id" : net_id})
        if student is None:
            return {}
        else:
            return student.get("late_days", {})

        # except Exception:
        #     if client:
        #         client.close()
            continue
    print('Failed to connect to cluster and get late days. Please post on Piazza.')
    return {}

def display_late_days_used():
    '''display_late_days_used() prints details about the number of late days used by the student'''
    late_days = get_late_days_used()
    print("Late Days used:")
    descriptors = ["P1","P2","P3","P4","P5","P6","P7","P8","P9","P10","P11","P12","P13"]
    total = 0
    exceeded_12 = False
    for i, descriptor in enumerate(descriptors):
        proj_num = str(i+1) # Important: project numbers are 1-indexed, and keys in MongoDB objects are strings
        if proj_num in late_days:
            ld = late_days[proj_num]
            total += ld
            if exceeded_12:
                ld = 0
            elif total > 12:
                ld = 12 - (total - ld)
                exceeded_12 = True
        else:
            ld = 0
        
        print(f"\t{descriptor} : {ld}")
    print("Keep in mind that you cannot use more than 3 late days on a single project")
    print("\nand that you cannot use more than 12 late days total.")
    print("\nAny additional late days used will result in a Late Day Deduction for that project.")

def get_score():
    '''get_score() returns the project score using the global variable `deductions`'''
    global deductions
    if FILE not in os.listdir(DIRECTORY):
        return 0
    nb = clean_nb(read_nb(os.path.join(DIRECTORY, FILE)))
    if nb['cells'][0]['cell_type'] == "raw" and nb['cells'][0]['source'].startswith('# ASSIGNMENT CONFIG'):
        return 127
    try:
        if FILE.split(".")[0][0].lower() == "p" and 2 <= int(FILE.split(".")[0][1:]) <= 13:
            make_late_day_deduction()
    except:
        pass
    score = int(TOTAL_SCORE - sum(list(deductions.values())))
    return min(max(0, score), TOTAL_SCORE)

def get_deduction_string():
    '''get_deduction_string() returns the deductions as a string in a suitable format'''
    global deductions, syntax_error_cells

    deductions_string = "Total Score: %d/%d" % (min(get_score(), TOTAL_SCORE), TOTAL_SCORE)
    if deductions != {}:
        deductions_string += "\nDeductions:\n"
        for qnum in deductions:
            deductions_string += "\t%s (-%d)\n" % (qnum, deductions[qnum])
        if syntax_error_cells == {}:
            deductions_string += "Scroll up to the individual tests for more TEST DETAILS\n"
        else:
            deductions_string += "Syntax Errors detected at the following cells:\n"
            for syntax_error in syntax_error_cells:
                deductions_string += "%s:%s\n" % (syntax_error, ("\n" + syntax_error_cells[syntax_error]).replace("\n", "\n\t|"))
            deductions_string += "These syntax errors are likely causing some hidden tests to crash, fix them and resubmit"
    return deductions_string

try:
    deductions = {}
    syntax_error_cells = {}
    rubric = parse_rubric_file(os.path.join(DIRECTORY, "rubric.md"))
    directories = get_directories(rubric, "hidden")
    comments = get_all_comments(directories)
except:
    pass
