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


def extract_config(FILE):
    '''extract the config data from the first cell of the master `nb`'''
    nb = read_nb(FILE)
    config_data = {}
    config = nb['cells'][0]['source'].split("\n")
    
    files = False
    autograder_files = False
    for line in config:
        if line.startswith('files:'):
            files = True
            config_data["files"] = []
            continue
        if files:
            if not line.startswith("    -"):
                files = False
            else:
                config_data["files"].append(line.strip(" -"))
                
        if line.startswith('autograder_files:'):
            autograder_files = True
            config_data["autograder_files"] = []
            continue
        if autograder_files:
            if not line.startswith("    -"):
                autograder_files = False
            else:
                config_data["autograder_files"].append(line.strip(" -"))
                
    return config_data


def parse_rubric(RUBRIC):
    '''reads `RUBRIC` and returns a dict mapping each rubric point to the points allotted to it'''
    f = open(RUBRIC, encoding='utf-8')
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
            if points == total_points and 'hardcode' in subdirectory:
                continue # this is to ensure that in p2, hardcode tests don't mess with the points for the other rubric items
            total_points -= points
    if total_points > 0:
        rubric[directory + ": public tests"] = total_points
        
    general_deductions = all_data[all_data.lower().find('general guidelines'):all_data.lower().find('question specific guidelines')]
    for line in general_deductions.split("\n"):
        if line.strip() == "":
            continue
        elif line.startswith("-"):
            directory = line.split("(")[0].strip(" -").replace("`", "")
            points = line.split("(")[1].split(")")[0].strip()
            if not points.replace("-", "").isnumeric():
                continue
            rubric["general_deductions: " + directory] = abs(int(points))
            
    return rubric


def copy_files(files, destination, readme_content):
    '''copies `files` to `destination` and also creates a README file at the `destination` with `readme_content` on it'''
    if os.path.exists(destination):
        shutil.rmtree(destination)
    os.mkdir(destination)
    
    for item in files:
        if os.path.isfile(item):
            shutil.copy(item, os.path.join(destination, os.path.basename(item)))
        elif os.path.isdir(item):
            shutil.copytree(item, os.path.join(destination, os.path.basename(item)))
        f = open(os.path.join(destination, "README.txt"), 'w', encoding='utf-8')
        f.write(readme_content + '\n')
        f.close()


def create_hidden_directory(FILE, DIRECTORY, RUBRIC):
    '''creates directories uses the `rubric` returned by `parse_rubric` and copies files
    to all the directories (along with the README), and finally returns a dictionary mapping
    each rubric point to the path of the directory corresponding to that rubric point'''
    hidden = os.path.join(DIRECTORY, "hidden")
    if os.path.exists(hidden):
        shutil.rmtree(hidden)
    os.mkdir(hidden)
    
    rubric = parse_rubric(RUBRIC)
    
    necessary_files = extract_config(FILE)['files']
    necessary_paths = [os.path.join(DIRECTORY, necessary_file) for necessary_file in necessary_files + ["answers.json"]]
    
    directories = {}

    directories["original"] = os.path.join(hidden, "original")
    copy_files(necessary_paths, directories["original"], "original")

    os.mkdir(os.path.join(hidden, "hardcode"))
    for i in range(1, 4):
        directories["hardcode: " + str(i)] = os.path.join(hidden, "hardcode", str(i))
        copy_files(necessary_paths, directories["hardcode: " + str(i)], 'hardcode: ' + str(i))

    subdirectories = {}
    for qnum in rubric:
        directory = qnum.split(':')[0]
        if directory not in subdirectories:
            subdirectories[directory] = 0
        if not os.path.exists(os.path.join(hidden, directory)):
            os.mkdir(os.path.join(hidden, directory))
        rubric_item = ":".join(qnum.split(':')[1:]).strip()
        if directory == "general_deductions" or rubric_item == "public tests":
            continue
        subdirectories[directory] += 1
        directories[qnum] = os.path.join(hidden, directory, str(subdirectories[directory]))
        copy_files(necessary_paths, directories[qnum], rubric_item)

    return directories


def create_hidden_tests_py(FILE, DIRECTORY):
    '''create `hidden_tests.py` by copying the functions from `hidden_tests.ipynb`
    with the relevant tags'''    
    sys_path = get_sys_path()
    tests_nb = read_nb(os.path.join(sys_path, 'templates', 'hidden_tests.ipynb'))
    necessary_files = extract_config(FILE)['files']
    
    f = open(os.path.join(get_sys_path(), "keys", "mongoDB-connection_string.txt"))
    mongoDB_URI = f.read()
    f.close()
    
    total_score = 100
    if os.path.basename(FILE).split(".")[0].lower().strip() == "p1":
        total_score = 25
    elif os.path.basename(FILE).split(".")[0].lower().strip() == "p9":
        total_score = 50
    
    tags = ['GENERAL', 'PLOTS'] if os.path.basename(FILE).split(".")[0] in ['p9', 'p11', 'p13'] else ['GENERAL']
    
    code = ""
    
    for idx in range(len(tests_nb['cells'])):
        tests_nb['cells'][idx]['source'] = tests_nb['cells'][idx]['source'].replace('NECESSARY_FILES = ...', 'NECESSARY_FILES = %s' % (repr(necessary_files)))
        tests_nb['cells'][idx]['source'] = tests_nb['cells'][idx]['source'].replace('FILE = ...', 'FILE = %s' % (repr(os.path.basename(FILE))))
        tests_nb['cells'][idx]['source'] = tests_nb['cells'][idx]['source'].replace('TOTAL_SCORE = ...', 'TOTAL_SCORE = %d' % (total_score))
        tests_nb['cells'][idx]['source'] = tests_nb['cells'][idx]['source'].replace('URI = ...', 'URI = %s' % (repr(mongoDB_URI)))
    
    for cell in tests_nb['cells']:
        if cell['cell_type'] != "code":
            continue
        text = cell['source'].split('\n')
        if text[0].replace('"', "") not in tags:
            continue
        code += "\n".join(text[1:])
        code += "\n"
    code = code[1:]
    file_locations = [os.path.join(DIRECTORY, 'hidden'), os.path.join(DIRECTORY, 'sandbox', 'autograder', 'hidden')]
    for location in file_locations:
        if not os.path.exists(location):
            continue
        f = open(os.path.join(location, 'hidden_tests.py'), 'w', encoding='utf-8')
        f.write(code)
        f.close()


def create_hidden_tests_ipynb(DIRECTORY):
    '''create base `hidden_tests.ipynb` without any tests by copying over from `hidden_tests_template.ipynb`'''
    sys_path = get_sys_path()
    tests_nb = read_nb(os.path.join(sys_path, 'templates', 'hidden_tests_template.ipynb'))
    file_locations = [os.path.join(DIRECTORY, 'hidden'), os.path.join(DIRECTORY, 'sandbox', 'autograder', 'hidden')]
    for location in file_locations:
        if not os.path.exists(location):
            continue
        with open(os.path.join(location, 'hidden_tests.ipynb'), 'w', encoding='utf-8') as f:
            nbformat.write(tests_nb, f)

def swap_qnum_directories(location, qnum_1, qnum_2):
    '''swap `qnum_1` with `qnum_2` in the hidden directories'''
    if not ((qnum_1[0] == "q" and qnum_1[1:].isdigit()) and (qnum_2[0] == "q" and qnum_2[1:].isdigit())):
        return
    if not os.path.exists(os.path.join(location, qnum_1)):
        if not os.path.exists(os.path.join(location, qnum_2)):
            return
        shutil.copytree(os.path.join(location, qnum_2), os.path.join(location, qnum_1))
        shutil.rmtree(os.path.join(location, qnum_2))
    elif not os.path.exists(os.path.join(location, qnum_2)):
        shutil.copytree(os.path.join(location, qnum_1), os.path.join(location, qnum_2))
        shutil.rmtree(os.path.join(location, qnum_1))
    else:
        if os.path.exists(os.path.join(location, "new_"+qnum_1)):
            shutil.rmtree(os.path.join(location, "new_"+qnum_1))
        shutil.copytree(os.path.join(location, qnum_1), os.path.join(location, "new_"+qnum_1))
        shutil.rmtree(os.path.join(location, qnum_1))
        shutil.copytree(os.path.join(location, qnum_2), os.path.join(location, qnum_1))
        shutil.rmtree(os.path.join(location, qnum_2))
        shutil.copytree(os.path.join(location, "new_"+qnum_1), os.path.join(location, qnum_2))
        shutil.rmtree(os.path.join(location, "new_"+qnum_1))

def swap_qnum_ipynb(tests_file, qnum_1, qnum_2):
    '''swap `qnum_1` with `qnum_2` in `hidden_tests.ipynb`'''
    if not ((qnum_1[0] == "q" and qnum_1[1:].isdigit()) and (qnum_2[0] == "q" and qnum_2[1:].isdigit())):
        return
    rubric_items = {qnum_1: [], qnum_2: []}
    nb = read_nb(tests_file)
    
    for start_idx, cell in enumerate(nb['cells']):
        if cell['cell_type'] == "markdown" and cell['source'].strip().startswith("## Rubric Tests"):
            break
    for idx in range(start_idx+2, len(nb['cells'])):
        cell = nb['cells'][idx]
        if not (cell['cell_type'] == "markdown" and ("\n" not in cell['source']) and cell['source'].startswith("###")):
            continue
        curr_qnum = cell['source'].strip(" #").split(":")[0].strip()
        if curr_qnum in [qnum_1, qnum_2]:
            rubric_items[curr_qnum].append(cell['source'].strip(" #"))
            
    for cell in nb['cells']:
        for curr_qnum in rubric_items:
            other_qnum = [qnum for qnum in rubric_items if qnum != curr_qnum][0]
            for rubric_item in rubric_items[curr_qnum]:
                cell['source'] = cell['source'].replace(rubric_item, rubric_item.replace(curr_qnum, other_qnum))
    with open(tests_file, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)

def swap_qnum(DIRECTORY, qnum_1, qnum_2):
    '''swap `qnum_1` with `qnum_2` in both `hidden_tests.ipynb` and the hidden directories'''
    file_locations = [os.path.join(DIRECTORY, 'hidden'), os.path.join(DIRECTORY, 'sandbox', 'autograder', 'hidden')]
    for location in file_locations:
        if not os.path.exists(location):
            continue
        swap_qnum_directories(location, qnum_1, qnum_2)
        swap_qnum_ipynb(os.path.join(location, "hidden_tests.ipynb"), qnum_1, qnum_2)

def rename_rubric_directories(directory, old_name, new_name):
    '''rename the rubric `old_name` to `new_name` in the hidden directories'''
    for item in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, item)):
            rename_rubric_directories(os.path.join(directory, item), old_name, new_name)
        if not (os.path.isfile(os.path.join(directory, item)) and item == "README.txt"):
            continue
        f = open(os.path.join(directory, item), encoding='utf-8')
        readme_data = f.read().split("\n")
        f.close()
        if readme_data[0].strip() == old_name:
            readme_data[0] = new_name
        f = open(os.path.join(directory, item), "w", encoding='utf-8')
        f.write("\n".join(readme_data))
        f.close()

def rename_rubric_ipynb(tests_file, old_rubric_item, new_rubric_item):
    '''rename the rubric `old_rubric_item` to `new_rubric_item` in `hidden_tests.ipynb`'''
    nb = read_nb(tests_file)
    for cell in nb['cells']:
        cell['source'] = cell['source'].replace(old_rubric_item, new_rubric_item)
    with open(tests_file, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f) 

def rename_rubric(DIRECTORY, old_rubric_item, new_rubric_item):
    '''rename the rubric `old_rubric_item` to `new_rubric_item` in `hidden_tests.ipynb`, as well as the hidden directories'''
    file_locations = [os.path.join(DIRECTORY, 'hidden'), os.path.join(DIRECTORY, 'sandbox', 'autograder', 'hidden')]
    for location in file_locations:
        if not os.path.exists(location):
            continue
        qnum = old_rubric_item.split(":")[0]
        old_name = old_rubric_item.split(":")[1].strip()
        new_name = new_rubric_item.split(":")[1].strip()
        rename_rubric_directories(os.path.join(location, qnum), old_name, new_name)
        rename_rubric_ipynb(os.path.join(location, "hidden_tests.ipynb"), old_rubric_item.strip(), new_rubric_item.strip())
        
def run_otter_tests(FILE, DIRECTORY, destination):
    '''run otter assign on FILE at `destination`'''
    nb = read_nb(FILE)
    try:
        ep = nbconvert.preprocessors.ExecutePreprocessor(timeout=300, kernel_name='python3')
        out = ep.preprocess(nb, {'metadata': {'path': DIRECTORY}})
    except Exception as e:
        print(e)
        return False
    
    with open(FILE, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)
    try:
        process = subprocess.run("otter assign %s %s" % (os.path.basename(FILE), destination), shell=True, cwd=DIRECTORY, capture_output=True)
        print(process.stderr.decode("utf-8"))
        return True
    except Exception as e:
        print(e)
        return False


def modify_sandbox_autograder(FILE, DIRECTORY, sandbox="sandbox"):
    '''modify the sandbox autograder file so that every time grader.check is called, the hidden tests are reset'''
    sandbox_file = os.path.join(DIRECTORY, sandbox, "autograder", os.path.basename(FILE))
    new_cells = []
    nb = read_nb(sandbox_file)
    for cell in nb['cells']:
        if cell['cell_type'] == "code" and "grader.check" in cell['source']:
            new_cells.append(new_code_cell("public_tests.reset_hidden_tests()"))
        new_cells.append(cell)
    nb['cells'] = new_cells
    with open(sandbox_file, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)


def generate_sandbox(FILE, DIRECTORY, sandbox="sandbox"):
    '''create a sandbox directory which can be used to create the hidden tests'''
    outcome = run_otter_tests(FILE, DIRECTORY, sandbox)
    if outcome:
        modify_sandbox_autograder(FILE, DIRECTORY, sandbox)


def gen_hidden_tests(FILE, DIRECTORY, RUBRIC, sandbox="sandbox"):
    DIRECTORY = os.path.dirname(FILE)
    create_hidden_directory(FILE, DIRECTORY, RUBRIC)
    print("hidden directory created")
    create_hidden_tests_py(FILE, DIRECTORY)
    print("`hidden_tests.py` created")
    create_hidden_tests_ipynb(DIRECTORY)
    print("`hidden_tests.ipynb` created")
    generate_sandbox(FILE, DIRECTORY, sandbox)
    print("sandbox directory created")
    if os.path.exists(os.path.join(DIRECTORY, "hidden")):
        shutil.rmtree(os.path.join(DIRECTORY, "hidden"))
