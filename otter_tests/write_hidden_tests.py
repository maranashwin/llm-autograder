import os, json, copy, nbformat, nbconvert, ast, shutil, sys, re
from nbformat.v4 import new_code_cell, new_markdown_cell, new_raw_cell, new_notebook
import openai


def get_sys_path():
    '''this helper function gets the path of the directory which contains the `otter_tests` directory'''
    for path in sys.path:
        otter_path = os.path.join(path, "otter_tests")
        if os.path.exists(otter_path):
            return otter_path


simple_model = "gpt-3.5-turbo-1106"
advanced_model = "gpt-4-1106-preview"

f = open(os.path.join(get_sys_path(), 'keys', 'gpt-key.txt'), encoding='utf-8')
openai.api_key = f.read().strip("\n ")
f.close()


def read_nb(file):
    '''read notebook file'''
    with open(file, encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)
    return nb


def write_nb(nb, file):
    '''write_nb(nb, file) and writes the contents of `nb` into `file`'''
    with open(file, "w", encoding='utf-8') as f:
        nbformat.write(nb, f)


def read_json(file):
    '''read json file'''
    f = open(file, encoding='utf-8')
    data = json.load(f)
    f.close()
    return data


def write_file_and_directory(FILE, TESTS):
    '''write FILE and DIRECTORY data to `hidden_tests.ipynb`'''
    tests = read_nb(TESTS)
    replacements = {'DIRECTORY = ...\nFILE = ...': 'DIRECTORY = %s\nFILE = %s' % (repr(".."), repr(os.path.basename(FILE)))}
    for cell in tests['cells']:
        if cell['cell_type'] != "code":
            continue
        for replacement in replacements:
            cell['source'] = cell['source'].replace(replacement, replacements[replacement])
    write_nb(tests, TESTS)


def get_required_function_names(FILE):
    '''read master FILE and extract data about required functions from markdown `Project Requirements` cell'''
    nb = read_nb(FILE)
    functions = []
    for cell in nb['cells']:
        if cell['cell_type'] != 'markdown':
            continue
        if '## Project Requirements' not in cell['source']:
            continue
        start_idx =  cell['source'].lower().find('required functions:')
        required_functions_text = cell['source'][start_idx:]
        for line in required_functions_text.split('\n')[1:]:
            if not line.strip().startswith('-'):
                break
            functions.append(line.strip("- ").split(" ")[0].strip(" -`"))
        
    return functions


def get_required_data_structure_names(FILE):
    '''read master FILE and extract data about required dat structures from markdown `Project Requirements` cell'''
    nb = read_nb(FILE)
    data_structures = []
    for cell in nb['cells']:
        if cell['cell_type'] != 'markdown':
            continue
        if '## Project Requirements' not in cell['source']:
            continue
        start_idx =  cell['source'].lower().find('required data structures:')
        required_functions_text = cell['source'][start_idx:]
        for line in required_functions_text.split('\n')[1:]:
            if not line.strip().startswith('-'):
                break
            data_structures.append(line.strip("- ").split(" ")[0].strip(" -`"))
        
    return data_structures


def get_all_functions(FILE):
    '''read master FILE and extract all functions (not just the required functions) defined inside'''
    nb = read_nb(FILE)
    functions = {}
    for cell in nb['cells']:
        if cell['cell_type'] != "code":
            continue
        try:
            code = ast.parse(cell['source'])
        except SyntaxError:
            continue
        for node in ast.walk(code):
            if isinstance(node, ast.FunctionDef):
                functions[node.name] = ast.unparse(code)
    return functions


def get_all_data_structures(FILE):
    '''read master FILE and extract all the required data structures defined inside'''
    nb = read_nb(FILE)
    data_structure_names = get_required_data_structure_names(FILE)
    data_structures = {data_structure: '' for data_structure in data_structure_names}
    for data_structure in data_structures:
        structure_begin = False
        for cell in nb['cells']:
            if cell['cell_type'] == 'raw' and 'name: %s' % (data_structure) in cell['source']:
                structure_begin = True
            if cell['cell_type'] == 'raw' and '# END SOLUTION' in cell['source']:
                structure_begin = False
            if cell['cell_type'] == "code" and structure_begin:
                data_structures[data_structure] += "\n" + ast.unparse(ast.parse(cell['source']))
    return data_structures            


def get_all_imports(FILE):
    '''read master FILE and extract all import statements inside'''
    nb = read_nb(FILE)
    imports = {}
    for cell in nb['cells']:
        if cell['cell_type'] != "code":
            continue
        try:
            code = ast.parse(cell['source'])
        except SyntaxError:
            continue
        for node in ast.walk(code):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            for import_statement in node.names:
                alias = import_statement.asname
                if alias == None:
                    alias = import_statement.name
                new_node = copy.deepcopy(node)
                new_node.names = [import_statement]
                imports[alias] = ast.unparse(new_node)
    return imports


def get_all_nested_dependencies(dependencies, name):
    '''use dictionary of dependencies to find all nested dependencies (i.e., dependencies of dependencies, etc)
    of given `name` in the `dependencies` dictionary'''
    old_dependencies = []
    new_dependencies = copy.copy(dependencies[name])
    while sorted(new_dependencies) != sorted(old_dependencies):
        old_dependencies = copy.copy(new_dependencies)
        for dependent in old_dependencies:
            new_dependencies.extend(dependencies[dependent])
        new_dependencies = list(set(new_dependencies))
    return old_dependencies        


def find_all_dependencies(FILE):
    '''read master FILE and extract all the dependencies of all functions and all required data structures
    with each other'''
    functions = get_all_functions(FILE)
    data_structures = get_all_data_structures(FILE)
    structres_and_functions = get_all_data_structures(FILE)
    structres_and_functions.update(functions)
    dependencies = {}
    for name in structres_and_functions:
        dependencies[name] = []
        for node in ast.walk(ast.parse(structres_and_functions[name])):
            if isinstance(node, ast.Call):
                dependent = ast.unparse(node.func)
                if dependent in functions and dependent != name:
                    dependencies[name].append(dependent)
            if isinstance(node, ast.Name):
                dependent = node.id
                if dependent in data_structures and dependent != name:
                    dependencies[name].append(dependent)
        dependencies[name] = list(set(dependencies[name]))
    for name in dependencies:
        dependencies[name] = get_all_nested_dependencies(dependencies, name)
    return dependencies


def get_self_contained_objects(FILE):
    '''read master FILE and generate self contained code for each required function and data structure
    so that the code does not need any other code apart from other required functions and data structures,
    in order to execute'''
    functions = get_all_functions(FILE)
    required_functions = get_required_function_names(FILE)
    data_structures = get_all_data_structures(FILE)
    structres_and_functions = copy.copy(data_structures)
    structres_and_functions.update(functions)
    dependencies = find_all_dependencies(FILE)
    imports = get_all_imports(FILE)
    self_contained_objects = {}
    for name in structres_and_functions:
        if name not in required_functions and name not in data_structures:
            continue
        self_contained_objects[name] = copy.copy(structres_and_functions[name])
        for dependent in dependencies[name]:
            if dependent in functions and dependent not in required_functions:
                self_contained_objects[name] = functions[dependent] + "\n\n" + self_contained_objects[name]
    for name in self_contained_objects:
        import_dependencies = []
        for node in ast.walk(ast.parse(self_contained_objects[name])):
            if not isinstance(node, ast.Call):
                continue
            for import_statement in imports:
                call_statement = ast.unparse(node.func)
                if call_statement.startswith(import_statement + ".") or call_statement == import_statement:
                    import_dependencies.append(imports[import_statement])
        import_dependencies = list(set(import_dependencies))
        for import_statement in import_dependencies:
            self_contained_objects[name] = import_statement + "\n" + self_contained_objects[name]
    return self_contained_objects


def get_self_contained_dependencies(FILE):
    '''read master FILE and extract all the dependencies of all required functions and required data structures
    with each other'''
    functions = get_all_functions(FILE)
    required_functions = get_required_function_names(FILE)
    data_structures = get_all_data_structures(FILE)
    dependencies = find_all_dependencies(FILE)
    self_contained_dependencies = {}
    for name in dependencies:
        if name not in required_functions and name not in data_structures:
            continue
        self_contained_dependencies[name] = []
        for dependent in dependencies[name]:
            if dependent not in required_functions and dependent not in data_structures:
                continue
            self_contained_dependencies[name].append(dependent)
    return self_contained_dependencies


def get_dependencies_text(variable, dependencies):
    '''generate the code to be injected into `hidden_tests.ipynb` to store the dependencies data'''
    text = '%s = {}\n' % (variable)
    for name in dependencies:
        text += '%s[%s] = %s\n' % (variable, repr(name), repr(dependencies[name]))
    text = text.strip("\n")
    return text


def write_dependencies(FILE, TESTS):
    '''read master FILE and write the dependencies data into TESTS'''
    tests = read_nb(TESTS)
    functions = get_required_function_names(FILE)
    data_structures = get_required_data_structure_names(FILE)
    dependencies = get_self_contained_dependencies(FILE)
    function_dependencies_functions = {}
    function_dependencies_data_structures = {}
    data_structure_dependencies_functions = {}
    data_structure_dependencies_data_structures = {}
    for name in dependencies:
        if name in functions:
            dependencies_functions = function_dependencies_functions
            dependencies_data_structures = function_dependencies_data_structures
        else:
            dependencies_functions = data_structure_dependencies_functions
            dependencies_data_structures = data_structure_dependencies_data_structures
        dependencies_functions[name] = []
        dependencies_data_structures[name] = []
        for dependent in dependencies[name]:
            if dependent in functions:
                dependencies_functions[name].append(dependent)
            else:
                dependencies_data_structures[name].append(dependent)
    replacements = {
        'function_dependencies_functions = ...': get_dependencies_text('function_dependencies_functions', function_dependencies_functions),
        'function_dependencies_data_structures = ...': get_dependencies_text('function_dependencies_data_structures', function_dependencies_data_structures),
        'data_structure_dependencies_functions = ...': get_dependencies_text('data_structure_dependencies_functions', data_structure_dependencies_functions),
        'data_structure_dependencies_data_structures = ...': get_dependencies_text('data_structure_dependencies_data_structures', data_structure_dependencies_data_structures)
    }
    for cell in tests['cells']:
        if cell['cell_type'] != "code":
            continue
        for replacement in replacements:
            cell['source'] = cell['source'].replace(replacement, replacements[replacement])
    write_nb(tests, TESTS)           


def add_test_segment(tests, tag, segment):
    '''helper function for adding cells into `hidden_tests.ipynb` file'''
    tests = copy.deepcopy(tests)
    start_idx, end_idx = None, None
    for idx in range(len(tests['cells'])):
        cell = tests['cells'][idx]
        if cell['cell_type'] != 'raw':
            continue
        if '# BEGIN %s' % (tag) in cell['source']:
            start_idx = idx
        if '# END %s' % (tag) in cell['source']:
            end_idx = idx
    tests['cells'] = tests['cells'][:start_idx+1] + segment + tests['cells'][end_idx:]
    return tests


def write_true_functions_and_data_structures(FILE, TESTS):
    '''read master FILE and extract the correct definitions of required functions and data structures
    and write it into TESTS'''
    tests = read_nb(TESTS)
    self_contained_objects = get_self_contained_objects(FILE)
    functions = get_required_function_names(FILE)
    data_structures = get_required_data_structure_names(FILE)
    function_cells = []
    function_cells.append(new_code_cell('true_functions = {}'))
    for function in functions:
        function_text = ast.unparse(ast.parse(self_contained_objects[function]))
        function_text = function_text.replace('"', '\\"').replace("'", "\\'")
        function_cells.append(new_code_cell('true_functions[%s] = """\n%s"""' % (repr(function), function_text)))
    tests = add_test_segment(tests, 'true_functions', function_cells)
    data_structure_cells = []
    data_structure_cells.append(new_code_cell('true_data_structures = {}'))
    for data_structure in data_structures:
        data_structure_text = ast.unparse(ast.parse(self_contained_objects[data_structure]))
        data_structure_text = data_structure_text.replace('"', '\\"').replace("'", "\\'")
        data_structure_cells.append(new_code_cell('true_data_structures[%s] = """\n%s"""' % (repr(data_structure), data_structure_text)))
    tests = add_test_segment(tests, 'true_data_structures', data_structure_cells)
    write_nb(tests, TESTS)


def ask_gpt(prompt, text, ALL_REPLIES, model=advanced_model):
    '''ask GPT for a reply given a system `prompt` and user `text`'''
    messages = [{"role": "system", "content": prompt}, {"role": "user", "content": text}]
    chat = openai.ChatCompletion.create(model=model, messages=messages)
    reply = chat.choices[0].message.content
    if not os.path.isfile(ALL_REPLIES):
        f = open(ALL_REPLIES, 'w', encoding='utf-8')
        f.close()
    f = open(ALL_REPLIES, 'a', encoding='utf-8')
    f.write('\n\n\n%s\n\n\n' % (reply))
    f.close()
    if '```python' in reply:
        reply = re.findall('```python(.*)```', reply, re.DOTALL)[0].strip('\n')
    return reply


def get_data_gen_text(FILE):
    '''read master FILE and extract the user text for random data generation to be provided to GPT'''
    nb = read_nb(FILE)
    data_gen_text = ''
    for cell in nb['cells']:
        if cell['cell_type'] != 'markdown':
            continue
        cell_details = cell['source'].lower().replace('ignore', '').strip('# \n')
        if cell_details.startswith('instructions for random data generation'):
            data_gen_text += cell['source'].replace('## IGNORE ##', '')
    return data_gen_text


# +
'''system prompt for random data generation to be provided to GPT'''

data_gen_prompt = """You are a TA for an introductory Python course.
You need to test students' code for a particular project.
You will do this by generating RANDOM datasets which are in the exact same format as the actual project dataset.
All the details about the dataset will be provided to you below.
You need to define a function called `random_data` which takes in two arguments.
The first argument `directory` is the path of the project directory.
All random files and directories must be generated inside this directory.
The second argument `n` represents the size of the random data generated.
It **must** use the default value that is provided as part of the instructions.
On execution, this function must create the random datasets exactly as described below.
Unless specified otherwise, each row of each column of each file must be chosen independently at random.
Whenever applicable, random names must be generated using the `Faker` module.
It is extremely important that the data is exactly in the format described below.
If the data files are already present in the given `directory`, the function must delete them first,
and then generate the random data. All files that are generated must explicitly have 'utf-8' encoding.
Any CSV file that is written must have the `newline=''` argument passed explicitly.
Any file or directory path string must be created using the `os.path.join` function instead of
hardcoding the slashes.
Your output must only be the Python code for this function's definition.
The code must be commented for clarity, but there should be no additional markdown text.
"""


# -

def get_data_gen_requirements(FILE):
    '''read master FILE and extract the requirements for random data generation to be written into `hidden_tests.ipynb`'''
    nb = read_nb(FILE)
    data_gen_requirements = []
    for cell in nb['cells']:
        if cell['cell_type'] != 'markdown':
            continue
        cell_details = cell['source'].lower().replace('ignore', '').strip('# \n')
        if cell_details.startswith('requirements for random data generation'):
            requirement_lines = cell['source'].split('\n')
            requirement_lines = [line for line in requirement_lines if not (line.startswith('#') or line.strip('# ') == '')]
            data_gen_requirements.append("\n".join(requirement_lines))
    return data_gen_requirements


def write_random_data(FILE, TESTS, ALL_REPLIES, overwrite=False, model=advanced_model):
    '''read master FILE and use GPT to define a function for generating random data, and write it into TESTS'''
    tests = read_nb(TESTS)
    for idx in range(len(tests['cells'])):
        cell = tests['cells'][idx]
        if cell['cell_type'] != 'markdown':
            continue
        if '## Random Data Generation' in cell['source']:
            break
    next_cell = tests['cells'][idx+1]
    if next_cell['cell_type'] == 'code' and 'def random_data' in next_cell['source']:
        if overwrite == False:
            return
        tests['cells'].pop(idx+1)
    gen_reply = ask_gpt(data_gen_prompt, get_data_gen_text(FILE), ALL_REPLIES, model)
    tests['cells'].insert(idx+1, new_code_cell(gen_reply))
    data_gen_requirements = get_data_gen_requirements(FILE)
    for requirement in data_gen_requirements:
        tests['cells'][idx]['source'] += "\n* %s" % (requirement)
    write_nb(tests, TESTS)


def parse_test_text(text):
    '''helper function for parsing the markdown test text in the master FILE'''
    lines = text.replace('IGNORE', '').strip('#\n ').split('\n')[1:]
    lines = [line for line in lines if line != ""]
    test_data = {}
    for line in lines:
        key = line.split(":")[0].strip('* ')
        value = line.split(":")[1].lstrip('* ').rstrip()
        if key == 'points':
            value = float(value)
        test_data[key] = value
    return test_data


def parse_questions(FILE):
    '''read the master FILE and parse all the markdown test text'''
    nb = read_nb(FILE)
    questions = {}
    curr_question = None
    tests_begin = False
    for cell in nb['cells']:
        if cell['cell_type'] == "raw" and '# BEGIN QUESTION' in cell['source']:
            curr_question = cell['source'].split('\n')[1].split(":")[1].strip()
        if cell['cell_type'] == "raw" and '# END QUESTION' in cell['source']:
            curr_question = None
        if curr_question == None:
            continue
        if curr_question not in questions:
            questions[curr_question] = {}
        if cell['cell_type'] == "raw" and '# BEGIN TESTS' in cell['source']:
            tests_begin = True
        if cell['cell_type'] == "raw" and '# END TESTS' in cell['source']:
            tests_begin = False
        if cell['cell_type'] == 'markdown' and not tests_begin:
            if 'question' not in questions[curr_question]:
                questions[curr_question]['question'] = ''
            questions[curr_question]['question'] += cell['source'] + "\n"
        if cell['cell_type'] == "code" and not tests_begin:
            if 'solution' not in questions[curr_question]:
                questions[curr_question]['solution'] = ''
            questions[curr_question]['solution'] += ast.unparse(ast.parse(cell['source'])) + "\n"
        if cell['cell_type'] == 'markdown' and tests_begin:
            test_type = cell['source'].replace('IGNORE', '').strip('#\n ').split('\n')[0]
            if test_type.lower() == 'public test':
                if 'public tests' not in questions[curr_question]:
                    questions[curr_question]['public tests'] = []
                questions[curr_question]['public tests'].append(parse_test_text(cell['source']))
            elif test_type.lower() == 'hidden test':
                if 'hidden tests' not in questions[curr_question]:
                    questions[curr_question]['hidden tests'] = []
                questions[curr_question]['hidden tests'].append(parse_test_text(cell['source']))
    return questions


def get_rubric(FILE):
    '''read the master FILE and extract the rubric items'''
    test_details = parse_questions(FILE)
    rubric = []
    for qnum in test_details:
        if 'hidden tests' not in test_details[qnum]:
            continue
        for hidden_test in test_details[qnum]['hidden tests']:
            rubric.append(qnum + ": " + hidden_test['rubric item'])
    return rubric


def write_empty_rubric(FILE, TESTS):
    '''read the master FILE and populate TESTS with starter cells for each rubric item'''
    tests = read_nb(TESTS)
    rubric = get_rubric(FILE)
    for idx, cell in enumerate(tests['cells']):
        if cell['cell_type'] == 'markdown' and '### Instructions for creating rubric tests:' in cell['source']:
            break
    tests['cells'] = tests['cells'][:idx+1]
    for rubric_item in rubric:
        tests['cells'].append(new_markdown_cell('### ' + rubric_item))
    write_nb(tests, TESTS)


# +
'''system prompt for dataset modifications for each rubric item to be provided to GPT'''

dataset_prompt = """You are a TA for an introductory Python course.
You need to test students' code for a particular question.
You will conduct this test by defining a function called `modify_data`
which takes in the argument `directory`, which is the path of the project
directory. This function when called, must modify the datasets in `directory`
as per the directions.
The format of the dataset, question and the correct solution
will be provided to you, as well as the particular rubric item
that is being tested.
You will also be provided with the details on what the `modify_data` function
needs to do.
If the test details say that any value must be randomized, then each such value
must be chosen independently at random.
If the test details say something about one column but not the others, it must
be assumed that the other columns take values in the correct format of the dataset.
After defining the function, you will then have to call some functions.
If the test details say that the dataset must be **completely modified**
using those precise words,
then the function `random_data` must be called.
This function has already been defined, so you must not redefine it.
This function takes in the project directory,
and the size of the data to be generated as its inputs.
As the first argument, you MUST pass the variable `directories[rubric_item]`.
The variables `directories` and `rubric_item` have also been already defined.
If the test details say how big the datasets must be, that number must be
passed as the second argument to `random_data`.
If no such information is provided, the default argument **must** be used.
Only **positional** arguments must be passed, not keyword arguments.
After calling `random_data`, the `modify_data` function must be called.
The variable `directories[rubric_item]` must again be passed as input to this function.
If the test details do **not** explicitly say that the dataset must be
**completely modified** using those precise words,
then the `random_data` function must NOT be called, but ONLY `modify_data`.
All files that are read or written must explicitly use 'utf-8' encoding.
All CSV files that are read must have the `newline=''` argument passed explicitly.
Any file or directory path string must be created using the `os.path.join` function instead of
hardcoding the slashes.
Your output must only be the Python code for this function's definition.
The code must be commented for clarity, but there should be no additional markdown text.
"""


# -

def get_dataset_text(FILE, rubric_item):
    '''read master FILE and extract the user text for dataset modification for `rubric_item` to be provided to GPT'''
    test_details = parse_questions(FILE)
    dataset_text = get_data_gen_text(FILE)
    dataset_text += "\n\n## TEST DETAILS: \n\n"
    qnum = rubric_item.split(":")[0].strip()
    qnum_details = test_details[qnum]
    if 'question' in qnum_details:
        dataset_text += 'QUESTION: %s\n\n' % (qnum_details['question'])
    if 'solution' in qnum_details:
        dataset_text += 'SOLUTION: %s\n\n' % (qnum_details['solution'])
    for hidden_test in qnum_details['hidden tests']:
        if not hidden_test['rubric item'] == rubric_item.split(":")[1].strip():
            continue
        dataset_text += "RUBRIC BEING TESTED: %s\n\n" % (rubric_item.split(":")[1].strip())
        dataset_text += "REASON FOR TEST: %s\n\n" % (hidden_test["reason for rubric"])
        if 'test dataset details' in hidden_test:
            dataset_text += "MODIFICATION DETAILS: %s" % (hidden_test['test dataset details'])
        else:
            dataset_text = "MODIFICATION DETAILS: the dataset is not modified"
    return dataset_text


def get_dataset_reply(FILE, ALL_REPLIES, rubric_item, model=advanced_model):
    '''read master FILE and use the system prompt and user text to ask GPT for code to modify dataset
    for testing `rubric_item`'''
    test_details = parse_questions(FILE)
    qnum = rubric_item.split(":")[0].strip()
    qnum_details = test_details[qnum]
    for hidden_test in qnum_details['hidden tests']:
        if hidden_test['rubric item'] == rubric_item.split(":")[1].strip():
            break
    if 'test dataset details' not in hidden_test:
        return None
    if 'save runtime'.replace(" ", "") in hidden_test['test dataset details'].replace(" ", "").lower():
        dataset_reply = 'random_data(directories[rubric_item], 100)'
    else:
        dataset_reply = ask_gpt(dataset_prompt, get_dataset_text(FILE, rubric_item), ALL_REPLIES, model)
    return dataset_reply


# +
'''system prompt for notebook modifcation for each rubric item to be provided to GPT'''

notebook_prompt = """You are a TA for an introductory Python course.
You need to test students' Python notebooks for a particular question,
function or data structure. You will test the code by modifying the student's 
notebook. You **must** only output Python code (WITHOUT any comments).
There should be NO text accompanying the code.
When you are provided with prior code already written
prior to the question being graded, you must make sure that any modifications
made for this test are consistent with the prior code. You are also **not**
allowed to assume that any files are folders are present in the project
directory other than those explicitly mentioned in the TEST DETAILS.
Importantly, this means that you cannot try to read any files that
are not EXPLICITLY mentioned as being a part of the dataset.

You are **not** allowed to directly modify the code yourself. Instead, you are
provided with some functions that have already been defined. You **must**
make all modifications to the notebook **only** using these functions:

* **`read_nb(file)`**: **reads** a `file` in the `.ipynb` file format and returns a `nb`.
    This function must be used to read the project file when it is required. The project file is
    found at the path `os.path.join(DIRECTORY, FILE)`. You may assume that the `os` module has already
    been imported and that the variables `DIRECTORY` and `FILE` have been defined already.
    example: `nb = read_nb(os.path.join(DIRECTORY, FILE))`

* **`clean_nb(nb)`**: standardizes the **format** of the `nb` so that it can be run.
    This function must always be called on the `nb` read using `read_nb`, unless the test details explicitly
    say that the notebook must be unmodified or used raw. In all other cases, this function must be called
    immediately after reading.
    example: `nb = clean_nb(nb)`
    
* **`run_nb(nb, file)`**: **executes** `nb` at the location `file`, **writes** the contents back into `file`, and also **returns** it.
    At the end of the test, after all modifications are made to the `nb`, this function must be run
    to run the `nb` at the project directory. The project directory will always be stored at the directory
    `os.path.join(directories[rubric_item], FILE)`.
    example: `nb = run_nb(nb, os.path.join(directories[rubric_item], FILE))`
    
* **`parse_nb(nb)`**: read the contents of a student `nb` and **extracts** all graded questions and answers.
    After running the `nb` with `run_nb`, this function is used to parse and grade the `nb` returned by `read_nb`.
    example: `results = parse_nb(nb)`
    
* **`find_all_cell_indices(nb, cell_type, marker)`**: returns **all** the indices in `nb` of cell type `cell_type` that **contains** the `marker` in its source.
    This function is used to identify all the indices of the cells in the student's `nb` which contain the given
    `marker` of the given `cell_type`. This function is really useful for identifying where a question begins or ends.
    In particular, to identify where a question (say question `q10`) **ends**, you can use
    `find_all_cell_indices(nb, "code", "grader.check('q10')")[-1]`. This is because at the end of each question,
    there will be a cell in the student's notebook which contains `grader.check('<question>')`. **Note the single quotes.**
    Similarly, if you want to identify the index where the function `function` ends, you can similarly use
    `find_all_cell_indices(nb, "code", "grader.check('function')")[-1]`.
    If you want to identify the index where the data structure `data_structure` ends, you can similarly use
    `find_all_cell_indices(nb, "code", "grader.check('data_structure')")[-1]`.
    The ONLY exception to this rule is if the QUESTION has the word "plot" in it. In the case of plot questions, the end
    of the question will be `get_first_plot_index(nb, start=find_all_cell_indices(nb, "code", "grader.check('q10')")[-1])`.
    The plot will be present somewhere after the `grader.check('<question>')` cell, and the `get_first_plot_index` function
    will identify the cell with the plot right after that `grader.check('<question>')` cell.    
    To identify the cell where a particular question (say question 'q10') **starts**, you can use the markdown QUESTION 
    provided to you as part of the input. For example, if the QUESTION is:
    `**Question 10:** Answer this question:`, you can use something like
    `find_all_cell_indices(nb, "markdown", '**Question 10:**')[-1]` to identify the cell containing this question. 
    
* **`truncate_nb(nb, start=None, end=None)`**: takes in a `nb`, and returns a **sliced** notebook between the cells indexed `start` and `end`.
    The default behavior for the `start` parameter is to not slice the notebook at the start, and the default behavior
    for the `end` parameter is to not slice the notebook at the end.
    This function is useful for saving runtime. If we are grading a particular question (say question `q4`), there is no
    reason to keep the cells of the notebook after the end of `q4`. So, right after reading and cleaning the notebook
    using `read_nb`, and `clean_nb`, it might make sense to truncate the notebook at the end.
    However, this function **must not** be called, if the test details explicitly say that the entire notebook is parsed,
    or that the notebook is not truncated.
    The `start` parameter should **never** be used to truncate the top of the notebook under any circumstances. Each
    question will use variables and functions defined earlier in the notebook, so truncating the top of the notebook
    will just cause the test to crash.
    example: `nb = truncate_nb(nb, end=find_all_indices(nb, "code", "grader.check('q4')")[-1])`.
    
* **`inject_code(nb, idx, code)`**: creates a **new** code cell in `nb` **at** the index `idx` with `code` in it.
    This function is useful for injecting our own code into the student's notebook, at any particular location.
    For example, if we want to inject the code `x = 0` after question `q2`, you can first use `find_all_cell_indices`
    to identify the index when `q4` ends and use `inject_code` to inject `x = 0` as follows.
    `nb = inject_code(nb, find_all_cell_indices(nb, "code", "grader.check('q4')")[-1], "x = 0")`
    You are NOT allowed to use this function to test the outputs of functions on given inputs. You **must** use the
    `inject_function_logic_check` function explained below for that purpose.
    
* **`replace_code(nb, target, new_code, start=None, end=None)`**: **replaces** all instances of the `target` in a code cell between the indices `start` and `end` with the `new_code`.
    The default behavior for the `start` parameter is to consider the notebook from the start, and the default behavior
    for the `end` parameter is to consider the notebook till the end.
    This function is useful for replacing all instances of some code in the `nb` with another. For example, if you
    want to replace all instances of the variable `var` with `new_var` in the entire notebook, you could use the default
    values with
    `nb = replace_code(nb, "var", "new_var")
    
* **`replace_with_false_function(nb, function, false_function)`**: **replaces** all definitions of `function` in the notebook with a new function `false_function`
    This function **must** be used when you are asked to replace a function definition. This function will identify
    all definitions of `function` in `nb` and replace them with the provided `false_function`. For example, if you had
    to replace a function `add(x, y)` with a function that found their difference, you could use
    ```
    new_add = '''
    def add(x, y):
        return x - y
    '''
    nb = replace_with_false_function(nb, 'add', new_add)
    ```
    
* **`replace_with_false_data_structure(nb, data_structure, false_data_structure)`**: **replaces** all definitions of `data_structure` in the notebook with a new data structure `false_data_structure`
    This function **must** be used when you are asked to replace a data structure definition. This function will identify
    all definitions of `data_structure` in `nb` and replace them with the provided `false_data_structure`. For example, if
    you had to replace a data structure `numbers_less_than_5` with a new data structure that stored only numbers less than 3,
    you could use
    ```
    new_numbers_less_than_5 = '''numbers_less_than_5 = [0, 1, 2]'''
    nb = false_data_structure(nb, 'numbers_less_than_5', new_numbers_less_than_5)
    ```
    In particular, if the TEST DETAILS say that you must first define the data strucutre correctly, then modify it, 
    `true_data_structures['<data_structure>']` must be added to the front of the `false_data_structure` argument.
    For example, if you are asked to define `numbers_less_than_5` and then modify it by sorting it in reverse,
    you could use
    ```
    new_numbers_less_than_5 = true_data_structures['numbers_less_than_5'] + '''
    numbers_less_than_5.sort(reverse=True)
    '''
    nb = false_data_structure(nb, 'numbers_less_than_5', new_numbers_less_than_5)
    ```
    
* **`inject_function_logic_check(nb, function, var_inputs_code, test_format)`**: **injects code to test whether `function` gives the same answer as expected on large inputs
    This function **must** be used when you are asked to test the outputs of any function. You **must** use this function
    explicitly when the question being tested is a `function`, and you are asked to test this `function` on various
    inputs. This function will automatically preprocess the `function` a little bit, and it will automatically
    inject the relevant code into the `nb` that will test the `function` on the provided inputs.
    The input arguments for this function need to be in a certain format. The variable `var_inputs_code` must be
    a string that defines a variable called `var_inputs` and assigns it be a list of all inputs. For example, 
    if we want the test the output of the function `add(x, y)` on the set of all inputs of `x` and `y` < 100, 
    we could define the variable to be
    ```
    var_inputs_code = '''
    from itertools import product
    var_inputs = list(product(list(range(100)), list(range(100))))
    '''
    ```
    or alternately
    ```
    var_inputs_code = '''
    var_inputs = []
    for x in range(100):
        for y in range(100):
            var_inputs.append((x, y))
    '''
    ```
    The value of the variable `var_inputs` should always be a list of tuples. Each tuple should contain the input
    arguments of the `function`.
    The value of the parameter `test_format` depends on the data type of the output of the function `function`.
    The various accepted `test_format` values are:
        "TEXT_FORMAT"  # when the expected output is a type, str, int, float, or bool
        "TEXT_FORMAT_UNORDERED_LIST"  # when the expected output is a list or a set where the order does *not* matter
        "TEXT_FORMAT_ORDERED_LIST"  # when the expected output is a list or tuple where the order **does** matter
        "TEXT_FORMAT_DICT"  # when the expected output is a dictionary
        "TEXT_FORMAT_NAMEDTUPLE"  # when the expected output is a namedtuple
        "HTML_FORMAT_ORDERED" # question type when the expected answer is a DataFrame and the order of the indices matter
        "HTML_FORMAT_UNORDERED" # question type when the expected answer is a DataFrame and the order of the indices does not matter
        "TEXT_FORMAT_SLASHES" # when the expected output is a str which contains file paths
        "TEXT_FORMAT_ORDERED_LIST_SLASHES"  # when the expected output is a list of file paths
    Putting this together, if you want to test the function `add(x, y)` on the set of all inputs of `x` and `y` < 100,
    you could use
    ```
    var_inputs_code = '''
    from itertools import product
    var_inputs = list(product(list(range(100)), list(range(100))))
    '''
    nb = inject_function_logic_check(nb, 'add', var_inputs_code, "TEXT_FORMAT")
    ```
    Similarly, if you are asked to test the outputs of a function `find_length` on inputs of strings of various lengths,
    you could use
    ```
    var_inputs_code = '''
    var_inputs = [('',), ('x',), ('xx',), ('xxx',), ('xxxx',), ('xxxxx',)]
    '''
    nb = inject_function_logic_check(nb, 'find_length', var_inputs_code, "TEXT_FORMAT")
    ```
    It is EXTREMELY IMPORTANT to use this function for testing functions instead of `code_inject`, because this
    function performs some additional preprocessing on the functions without which the tests would not work.

* **`inject_data_structure_check(nb, data_structure, test_format)`**: **injects code to test whether `data_structure` has the same value as expected
    This function **must** be used when you are asked to test the value of any data structure.
    This function automatically preprocessed the `data_structure` and injects code to the notebook to test
    whether the value of the `data_structure` is correct. The argument `test_format`
    must be of the same format as in the `inject_function_logic_check` function. For example, if you want to check if the
    data structure `numbers_less_than_5` has the expected value, you could use
    `nb = inject_data_structure_check(nb, 'numbers_less_than_5', "TEXT_FORMAT")`
    
* **`get_test_text(qnum, test_code)`**: specifically creates wrapper for `test_code` so it can be used for testing `qnum`.
    If you are **specifically** asked to inject some code to **test** a question, you must use this function to
    modify the `test_code` before you inject. When a question is being tested (such as `q1`, or `q20`), then the argument
    to be passed as `qnum` is just `'q1'` or `'q20'`. But if the question being tested is a function or a data structure
    (say `add` or `numbers_less_than_5`), then only the name of the function or data structure must be passed as the
    argument. In this case, it should be `'add'` or `'numbers_less_than_5'`. Note that the backticks should not
    be passed inside the string as part of the input.
    
    For example, if you need to inject some code to test `q1` by checking if
    the variable `numbers_less_than_5` has the correct value, you will need to do something like:
    ```
    test_code = '''
    if public_tests.compare([0, 1, 2, 3, 4], numbers_less_than_5, "TEXT_FORMAT_UNORDERED_LIST") == public_tests.PASS:
        test_output = 'q1 results: ' + public_tests.PASS
    '''
    nb = inject_code(nb, len(nb['cells']), get_test_text("q1", test_code))
    ```
    
    The variable `test_code` as in the example above needs to be in a very specific format. It needs to use the
    `public_tests.compare` function to perform all comparisons. The first argument for this function must be the
    expected outcome. The second argument is the variable that is being tested, and the third argument is the
    `test_format` which follows the same rules as above. The comparison is successful if the output of
    `public_tests.compare` is `public_tests.PASS`. If all the required comparisons for the test pass, the variable
    `test_output` **must** be assigned the value in the format above.
    If any of the required comparisons fail, the variable `test_output` must **not** be defined at all.
    The variable must only be defined (and it must be defined as in the example above as
    "<qnum> results: All test cases passed!") ONLY if the test cases pass. Otherwise, it must not be defined at all.
    The `get_test_code` function is then used to wrap the `test_code` with some extra code needed for the test to work.
    Note that in the `inject_code` function, we are passing `len(nb['cells'])` as the input for the `idx` argument.
    This is what we must always do while injecting code to test a question, as it will ensure that the code is
    injected at the very end of the notebook.
    
    Here is another example. Let us say we need to test whether `x` has the value 5, and `y` has the value 0 to test `q8`,
    you could use
    ```
    test_code = '''
    if public_tests.compare(5, x, "TEXT_FORMAT") == public_tests.PASS:
        if public_tests.compare(0, y, "TEXT_FORMAT") == public_tests.PASS:
            test_output = 'q8 results: ' + public_tests.PASS
    '''
    nb = inject_code(nb, len(nb['cells']), get_test_text("q8", test_code))
    ```
    
You **must** use the functions provided above to modify the notebook as per the test details provided to you. Your goal is
to first read, clean, and truncate the notebook until the question being tested, then modify the notebook as required 
by the test, and finally run, and parse the output, and store the outcome in the variable `results[rubric_item]`.
You may assume that the variable `rubric_item` has already been defined for you.

For example, if you are asked to replace a data structure (say `numbers_less_than_5`) with a data structure that behaves
differently, you will need to define a new data structure that not only behaves differently, but gives a meaningful
**non-trivial** output for the given question. For example, if the question you are being asked to test is
`q10`, and in the solution, `numbers_less_than_5` is used to detect how many numbers less than 5 and more than 2,
you need to replace `numbers_less_than_5` with a data structure that contains numbers more than 5 and also does not
include some numbers between 2 and 5, as in the example below:
```
nb = read_nb(os.path.join(DIRECTORY, FILE))
nb = clean_nb(nb)
nb = truncate_nb(nb, end=find_all_cell_indices(nb, "code", "grader.check('q10')")[-1])

new_numbers_less_than_5 = '''numbers_less_than_5 = [0, 1, 2, 3, 6]'''
nb = false_data_structure(nb, 'numbers_less_than_5', new_numbers_less_than_5)

results[rubric_item] = parse_nb(run_nb(nb, os.path.join(directories[rubric_item], FILE)))
```

On the other hand, if you are asked to replace a function (say `add`) with a function that behaves differently, you will
need to define a new function that not only behaves differently, but gives a valid output for the given question. For example,
if the question you are being asked to test is `q5`, and in the solution, `add` is used to find the sum of two numbers,
you need to replace `add` with a function which takes in two numbers, but computes something **non-trivial** 
other than the sum, as in the example below:
```
nb = read_nb(os.path.join(DIRECTORY, FILE))
nb = clean_nb(nb)
nb = truncate_nb(nb, end=find_all_cell_indices(nb, "code", "grader.check('q5')")[-1])

new_add = '''
def add(x, y):
    return x - y
'''
nb = replace_with_false_function(nb, 'add', new_add)

results[rubric_item] = parse_nb(run_nb(nb, os.path.join(directories[rubric_item], FILE)))
```

If you are asked to replace a function `add` with a function that finds the difference and then test the output of
the **function** `find_sum_of_three_numbers` by testing it on inputs of all `x`, `y`, `z` < 10, you must do
```
nb = read_nb(os.path.join(DIRECTORY, FILE))
nb = clean_nb(nb)
nb = truncate_nb(nb, end=find_all_cell_indices(nb, "code", "grader.check('find_sum_of_three_numbers')")[-1])

new_add = '''
def add(x, y):
    return x - y
'''
nb = replace_with_false_function(nb, 'add', new_add)

var_inputs_code = '''
var_inputs = []
for x in range(10):
    for y in range(10):
        for z in range(10):
            var_inputs.append((x, y, z))
'''
nb = inject_function_logic_check(nb, 'find_sum_of_three_numbers', var_inputs_code, 'TEXT_FORMAT')

results[rubric_item] = parse_nb(run_nb(nb, os.path.join(directories[rubric_item], FILE)))
```
"""


# -

def get_notebook_text(FILE, rubric_item):
    '''read master FILE and extract the user text for notebook modification for `rubric_item` to be provided to GPT'''
    test_details = parse_questions(FILE)
    self_contained_objects = get_self_contained_objects(FILE)
    self_contained_dependencies = get_self_contained_dependencies(FILE)
    self_contained_objects = get_self_contained_objects(FILE)
    self_contained_dependencies = get_self_contained_dependencies(FILE)
    dependent_text = ''
    for item in re.findall('`([^`]*)`', rubric_item):
        if item not in self_contained_objects:
            continue
        for dependent in self_contained_dependencies[item]:
            dependent_text += self_contained_objects[dependent] + "\n"
        dependent_text += self_contained_objects[item]
    
    notebook_text = "\n\n## TEST DETAILS: \n\n"
    qnum = rubric_item.split(":")[0].strip()
    qnum_details = test_details[qnum]
    if 'question' in qnum_details:
        notebook_text += 'QUESTION: %s\n\n' % (qnum_details['question'])
    if dependent_text != "":
        notebook_text += 'PRIOR CODE USED FOR DEFINING FUNCTIONS AND DATA STRUCTURES:\n%s\n\n' % (dependent_text)
    if 'solution' in qnum_details:
        notebook_text += 'SOLUTION:\n%s\n\n' % (qnum_details['solution'])
    for hidden_test in qnum_details['hidden tests']:
        if not hidden_test['rubric item'] == rubric_item.split(":")[1].strip():
            continue
        notebook_text += "RUBRIC BEING TESTED: %s\n\n" % (rubric_item.split(":")[1].strip())
        notebook_text += "REASON FOR TEST: %s\n\n" % (hidden_test["reason for rubric"])
        if 'test notebook details' in hidden_test:
            notebook_text += "MODIFICATION DETAILS: %s" % (hidden_test['test notebook details'])
        else:
            notebook_text += "MODIFICATION DETAILS: the notebook is not modified"
    return notebook_text


def get_notebook_reply(FILE, ALL_REPLIES, rubric_item, model=advanced_model):
    '''read master FILE and use the system prompt and user text to ask GPT for code to modify notebook
    for testing `rubric_item`'''
    qnum = rubric_item.split(":")[0].strip()
    header_code = "rubric_item = '%s'\n" % (rubric_item.replace('"', '\\"').replace("'", "\\'"))
    default_output = "nb = clean_nb(read_nb(os.path.join(DIRECTORY, FILE)))\n"
    default_output += "nb = truncate_nb(nb, end=find_all_cell_indices(nb, \"code\", \"grader.check('%s')\")[-1])\n" % (qnum)
    default_output += "\nresults[rubric_item] = parse_nb(run_nb(nb, os.path.join(directories[rubric_item], FILE)))"
    test_details = parse_questions(FILE)
    qnum = rubric_item.split(":")[0].strip()
    qnum_details = test_details[qnum]
    for hidden_test in qnum_details['hidden tests']:
        if not hidden_test['rubric item'] == rubric_item.split(":")[1].strip():
            continue
        if 'test notebook details' not in hidden_test:
            return header_code + default_output
    notebook_reply = ask_gpt(notebook_prompt, get_notebook_text(FILE, rubric_item), ALL_REPLIES, model)
    return header_code + notebook_reply


# +
'''system prompt for error message to be provided to students for each rubric item to be provided to GPT'''

rubric_prompt = """
You are a grader for an introductory Python course. A student has turned in a
solution to a problem that passes their local tests. Your instructor has
written code for testing this question. He may have run the student's
code on a different dataset, or made some modifications to the student's notebook
before executing it.
Your job is to provide feedback to students who have failed the test.
You will be provided with the question, and the correct solution for reference.
You will also be told the reason behind the test, and how the test is conducted.
You must assume that the students are beginners who do not know anything
about Python more than what is in the expected SOLUTION for this question.
You need to provide them with a short helpful description of how the test
was conducted and what they can do to fix their code.
You must NEVER give a specific reason for why they failed the test
with certainty. Instead, you must merely suggest possibities.
Your feedback should be formal, and should not have any pleasantries.
It should be short and to the point. Your reply should use less than 60 words."""


# -

def get_rubric_text(FILE, rubric_item):
    '''read master FILE and extract the user text for test details for `rubric_item` to be provided to GPT'''
    test_details = parse_questions(FILE)
    rubric_text = "\n\n## TEST DETAILS: \n\n"
    qnum = rubric_item.split(":")[0].strip()
    qnum_details = test_details[qnum]
    if 'question' in qnum_details:
        rubric_text += 'QUESTION: %s\n\n' % (qnum_details['question'])
    if 'solution' in qnum_details:
        rubric_text += 'SOLUTION:\n%s\n\n' % (qnum_details['solution'])
    for hidden_test in qnum_details['hidden tests']:
        if not hidden_test['rubric item'] == rubric_item.split(":")[1].strip():
            continue
        rubric_text += "RUBRIC BEING TESTED: %s\n\n" % (rubric_item.split(":")[1].strip())
        rubric_text += "REASON FOR TEST: %s\n\n" % (hidden_test["reason for rubric"])
        if 'test dataset details' in hidden_test:
            rubric_text += "DATASET MODIFICATION DETAILS: %s" % (hidden_test['test dataset details'])
        if 'test notebook details' in hidden_test:
            rubric_text += "NOTEBOOK MODIFICATION DETAILS: %s" % (hidden_test['test notebook details'])
    return rubric_text


def split_into_short_lines(input_string, max_line_length=50):
    '''helper function for splitting up test details into short lines'''
    words = input_string.split()
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_line_length:
            if current_line:
                current_line += " "
            current_line += word
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)
    return "\n".join(lines)


def get_rubric_reply(FILE, ALL_REPLIES, rubric_item, model=advanced_model):
    '''read master FILE and use the system prompt and user text to ask GPT for test details provided 
    to students for `rubric_item`'''
    rubric_code = "rubric_item = '%s'\n" % (rubric_item.replace('"', '\\"').replace("'", "\\'"))
    rubric_reply = ask_gpt(rubric_prompt, get_rubric_text(FILE, rubric_item), ALL_REPLIES, model)
    rubric_code += "readme_text = \"\"\"%s\"\"\"\n\n" % (split_into_short_lines(rubric_reply))
    rubric_code += "write_readme(readme_text, os.path.join(directories[rubric_item], \"README.txt\"))"
    return rubric_code


def get_gen_public_tests_reply():
    '''generate code for generating public tests'''
    return "gen_public_tests.gen_public_tests(os.path.join(directories[rubric_item], FILE))"


def write_rubric_test(FILE, TESTS, ALL_REPLIES, rubric_item, overwrite=False, model=advanced_model):
    '''read master FILE and use GPT to generate code for testing `rubric_item`, and write it into TESTS'''
    if 'general_deductions' in rubric_item:
        return
    tests = read_nb(TESTS)
    found = False
    for start_idx, cell in enumerate(tests['cells']):
        if cell['cell_type'] == 'markdown' and ('### ' + rubric_item) in cell['source']:
            found = True
            break
    if not found:
        return
    start_idx = start_idx + 1
    if start_idx < len(tests['cells']) and tests['cells'][start_idx]['cell_type'] != "markdown":
        if overwrite == False:
            return
        for end_idx in range(start_idx, len(tests['cells'])):
            if tests['cells'][end_idx]['cell_type'] == "markdown":
                break
        tests['cells'] = tests['cells'][:start_idx] + tests['cells'][end_idx:]
    rubric_item_cells = []
    rubric_reply = get_rubric_reply(FILE, ALL_REPLIES, rubric_item, model)
    rubric_item_cells.append(new_code_cell(rubric_reply))
    dataset_reply = get_dataset_reply(FILE, ALL_REPLIES, rubric_item, model)
    if dataset_reply != None:
        rubric_item_cells.append(new_code_cell(dataset_reply))
    rubric_item_cells.append(new_raw_cell('# BEGIN %s' % (rubric_item)))
    notebook_reply = get_notebook_reply(FILE, ALL_REPLIES, rubric_item)
    rubric_item_cells.append(new_code_cell(notebook_reply))
    rubric_item_cells.append(new_raw_cell('# END %s' % (rubric_item)))
    gen_public_tests_reply = get_gen_public_tests_reply()
    rubric_item_cells.append(new_code_cell(gen_public_tests_reply))
    tests['cells'] = tests['cells'][:start_idx] + rubric_item_cells + tests['cells'][start_idx:]
    write_nb(tests, TESTS)


def write_base_hidden_tests(FILE, TESTS):
    '''read master FILE and write all necessary data into TESTS that does not require GPT assistance'''
    write_file_and_directory(FILE, TESTS)
    write_dependencies(FILE, TESTS)
    write_true_functions_and_data_structures(FILE, TESTS)
    tests = read_nb(TESTS)
    empty_rubric = False
    for idx in range(-1, -5, -1):
        cell = tests['cells'][idx]
        if cell['cell_type'] == 'markdown' and '### Instructions for creating rubric tests:' in cell['source']:
            empty_rubric = True
    if empty_rubric == True:
        write_empty_rubric(FILE, TESTS)


def refresh_hidden_tests_ipynb(FILE, TESTS):
    '''refresh TESTS and delete tests no longer in master FILE, and add new tests in FILE to TESTS'''
    tests = read_nb(TESTS)
    rubric = get_rubric(FILE)
    for idx, cell in enumerate(tests['cells']):
        if cell['cell_type'] == 'markdown' and '### Instructions for creating rubric tests:' in cell['source']:
            break
    old_test_cells = tests['cells'][idx+1:]
    old_tests = {}
    curr_test = None
    for test_cell in old_test_cells:
        if test_cell['cell_type'] == 'markdown':
            curr_test = test_cell['source'].strip('# \n')
        if curr_test == None:
            continue
        if curr_test not in old_tests:
            old_tests[curr_test] = []
        old_tests[curr_test].append(test_cell)
    
    new_test_cells = tests['cells'][:idx+1]
    for rubric_item in rubric:
        if rubric_item in old_tests:
            new_test_cells.extend(old_tests[rubric_item])
        else:
            new_test_cells.append(new_markdown_cell('### ' + rubric_item))
    tests['cells'] = new_test_cells
    write_nb(tests, TESTS)


def write_latest_rubric_test(FILE, TESTS, ALL_REPLIES):
    '''read master FILE and use it to generate tests for next rubric item in TESTS that is still empty'''
    tests = read_nb(TESTS)
    rubric = get_rubric(FILE)
    for start_idx, cell in enumerate(tests['cells']):
        if cell['cell_type'] == 'markdown' and '### Instructions for creating rubric tests:' in cell['source']:
            break
    for idx in range(start_idx+1, len(tests['cells'])):
        cell = tests['cells'][idx]
        if cell['cell_type'] == 'markdown' and cell['source'].strip(' #') in rubric:
            if idx + 1 < len(tests['cells']) and tests['cells'][idx + 1]['cell_type'] == 'markdown':
                break
    if idx + 1 == len(tests['cells']):
        return False
    rubric_item = cell['source'].strip(' #')
    write_rubric_test(FILE, TESTS, ALL_REPLIES, rubric_item)
    return rubric_item


def write_hidden_tests(FILE, TESTS, ALL_REPLIES):
    '''read master FILE and use it to generate tests for all empty rubric items in TESTS'''
    halt = False
    while halt == False:
        halt = write_latest_rubric_test(FILE, TESTS, ALL_REPLIES)
