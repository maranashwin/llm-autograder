import os, sys, nbformat, nbconvert, copy, ast, json
from nbformat.v4 import new_code_cell, new_markdown_cell, new_raw_cell, new_notebook


def read_nb(file):
    '''read notebook file'''
    with open(file, encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)
    return nb


def write_nb(nb, file):
    '''write_nb(nb, file) and writes the contents of `nb` into `file`'''
    with open(file, "w", encoding='utf-8') as f:
        nbformat.write(nb, f)


def extract_tests(FILE):
    '''parse FILE and identify all cells inside raw # BEGIN TESTS and # END TESTS tags'''
    nb = read_nb(FILE)
    tests = {}
    qnum = None
    test_cell = False
    for cell in nb['cells']:
        if cell['cell_type'] == "raw" and '# BEGIN QUESTION' in cell['source']:
            qnum = cell['source'].split('\n')[1].split(':')[1].strip()
            tests[qnum] = []
        elif cell['cell_type'] == "raw" and '# END QUESTION' in cell['source']:
            qnum = None
        if qnum == None:
            continue
        if cell['cell_type'] == "raw" and '# BEGIN TESTS' in cell['source']:
            test_cell = True
        elif cell['cell_type'] == "raw" and '# END TESTS' in cell['source']:
            test_cell = False
        elif test_cell == True:
            tests[qnum].append(cell)
    return tests


def parse_test_text(text):
    '''given `text` from inside a markdown test cell, parse the data and return a dictionary with all relevant data'''
    lines = text.replace('IGNORE', '').strip('#\n ').split('\n')
    lines = [line for line in lines if line != ""]
    test_data = {}
    test_data['test type'] = lines[0].lower()
    lines = lines[1:]
    for line in lines:
        key = line.split(":")[0].strip('* ')
        value = ":".join(line.split(":")[1:]).lstrip('* ').rstrip()
        if key == 'points':
            value = float(value)
        test_data[key] = value
    return test_data


def get_public_test_code(qnum, test_details):
    '''given a `qnum` and `test_details` for the public test of that `qnum`, return the code that should be added to FILE
    for this public test'''
    if 'answer' not in test_details:
        return None
    question = test_details['answer']
    if 'question' in test_details:
        question = test_details['question']
    test_code = 'public_tests.check(%s, %s)' % (repr(qnum), question)
    return test_code


def get_hidden_test_code(FILE, qnum, test_details):
    '''given a `qnum` and `test_details` for a hidden test of that `qnum`, return the code that should be added to FILE
    for this hidden test'''
    rubric_item = '%s: %s' % (qnum, test_details['rubric item'].replace('"', '\"').replace("'", "\'"))
    points = test_details['points']
    rubric_message = "Note that the Gradescope autograder will deduct points if your code fails the following rubric point - "
    rubric_message += "'%s (-%g)'." % (test_details['rubric item'].replace(":", "-"), points)
    rubric_message += "The public tests cannot determine if your code satisfies these requirements. Verify your code manually."
    test_code = '''\"\"\" # BEGIN TEST CONFIG\nsuccess_message: %s\n\"\"\" # END TEST CONFIG\n\n''' % (rubric_message)
    test_code += "public_tests.rubric_check(%s)" % (repr(rubric_item))
    return test_code


def get_test_code(FILE, qnum, text):
    '''given a `qnum` and `text` from inside a markdown test cell, return the code that should be added to FILE
    for this test (public or hidden)'''
    test_details = parse_test_text(text)
    if test_details['test type'] == 'public test':
        return get_public_test_code(qnum, test_details)
    elif test_details['test type'] == 'hidden test':
        return get_hidden_test_code(FILE, qnum, test_details)
    elif test_details['test type'] == 'dummy test':
        return "print('All test cases passed!')"


def parse_hidden_test_code(test_code):
    '''given some `test_code` from inside a code test cell, identify if it is for a hidden test, and identify the rubric
    being tested by this code'''
    if test_code == None:
        return
    for node in ast.walk(ast.parse(test_code)):
        try:
            if not isinstance(node, ast.Call):
                continue
            if ast.unparse(node.func.value) != 'public_tests':
                continue
            if node.func.attr == "rubric_check":
                return node.args[0].value.split(":")[1].strip()
        except:
            continue


def extract_code_in_tests(FILE):
    '''identify all the code test cells that are already in the FILE for each question,
    and return a dictionary with this data'''
    tests = extract_tests(FILE)
    code_in_tests = {}
    for qnum in tests:
        code_in_tests[qnum] = {}
        for test_cell in tests[qnum]:
            if test_cell['cell_type'] != "code":
                continue
            code_in_tests[qnum][parse_hidden_test_code(test_cell['source'])] = test_cell['source']
    return code_in_tests


def get_summary_test(FILE):
    '''return the test cells for displaying the summary and calculating the score'''
    test_cells = []
    test = '''\"\"\" # BEGIN TEST CONFIG\npoints: 0\nhidden: true\n\"\"\" # END TEST CONFIG\n\n'''
    test += "public_tests.detect_public_tests()"
    test_cells.append(new_code_cell(test))
    for digit in range(6, -1, -1):
        test = '''\"\"\" # BEGIN TEST CONFIG\npoints: %s\nhidden: true\n\"\"\" # END TEST CONFIG\n\n''' % (2**digit)
        test += "public_tests.get_score_digit(%s) == 1" % (digit)
        test_cells.append(new_code_cell(test))
    summary_message = "Please submit your zip folder to Gradescope, and check your final score there. "
    summary_message += "The Gradescope autograder will make deductions to your score based on the rubric."
    test = '''\"\"\" # BEGIN TEST CONFIG\nsuccess_message: %s\n\"\"\" # END TEST CONFIG\n\n''' % (summary_message)
    test += "public_tests.get_summary()"
    test_cells.append(new_code_cell(test))
    if os.path.basename(FILE).split(".")[0].lower().strip() == "p1":
        late_day_message = "The total number of late days you have used for all projects in this course "
        late_day_message += "will be displayed on Gradescope when you submit."
        test = '''\"\"\" # BEGIN TEST CONFIG\nsuccess_message: %s\n\"\"\" # END TEST CONFIG\n\n''' % (late_day_message)
        test += "public_tests.display_late_days_used()"
        test_cells.append(new_code_cell(test))
    return test_cells


def update_tests(FILE, refresh=False):
    '''add the necessary code test cells to FILE that are not already there; if `refresh` is set to `True`,
    then refresh old code test cells also'''
    tests = extract_tests(FILE)
    code_in_tests = extract_code_in_tests(FILE)
    for qnum in tests:
        points = 0
        new_tests = []
        for test_cell in tests[qnum]:
            if test_cell['cell_type'] != 'markdown':
                continue
            new_tests.append(test_cell)
            test_details = parse_test_text(test_cell['source'])
            if test_details['test type'] == 'public test':
                points = test_details['points']
            else:
                points -= test_details['points']
            test_code = get_test_code(FILE, qnum, test_cell['source'])
            if 'rubric item' in test_details and test_details['rubric item'] in code_in_tests[qnum]:
                if refresh == False:
                    test_code = code_in_tests[qnum][test_details['rubric item']]
            if test_code != None:
                new_tests.append(new_code_cell(test_code))
        if points > 0:
            rubric_item = '%s: public tests' % (qnum)
            test_code = 'public_tests.rubric_check(%s)' % (repr(rubric_item))
            new_tests.append(new_code_cell(test_code))
        tests[qnum] = new_tests
        if qnum == 'summary':
            tests[qnum] = get_summary_test(FILE)
    return tests


def correct_points(FILE):
    '''correct the `points` data in the raw cells of each question in FILE'''
    nb = read_nb(FILE)
    for cell in nb['cells']:
        if cell['cell_type'] != "raw":
            continue
        if '# BEGIN QUESTION' not in cell['source']:
            continue
        lines = cell['source'].split('\n')
        if lines[1].split(":")[1].strip() == "summary":
            lines[2] = "points: 127"
        else:
            lines[2] = "points: 0"
        cell['source'] = "\n".join(lines)
    write_nb(nb, FILE)


def check_nb(FILE):
    '''check if the file is in the correct format'''
    nb = read_nb(FILE)
    for cell in nb['cells']:
        if cell['cell_type'] != "code":
            continue
        try:
            ast.parse(cell['source'])
        except SyntaxError:
            if '%matplotlib inline' not in cell['source']:
                return 'SyntaxError detected:\n %s' % (cell['source'])
    last_qnum = None
    qnum = None
    solution = []
    curr_solution = False
    tests = []
    curr_test = False
    for cell in nb['cells']:
        if cell['cell_type'] != "raw":
            continue
        if '# BEGIN QUESTION' in cell['source']:
            if qnum != None:
                return "extra '# BEGIN QUESTION' detected inside QUESTION %s" % (qnum)
            qnum = cell['source'].split('\n')[1].split(":")[1].strip()
        elif '# END QUESTION' in cell['source']:
            if qnum == None:
                if last_qnum == None:
                    return "exta '# END QUESTION' detected before any '# BEGIN QUESTION'"
                else:
                    return "extra '# END QUESTION' detected after QUESTION %s" % (last_qnum)
            last_qnum = qnum
            qnum = None
        elif '# BEGIN SOLUTION' in cell['source']:
            if qnum == None:
                if last_qnum == None:
                    return "exta '# BEGIN SOLUTION' detected before any '# BEGIN QUESTION'"
                else:
                    return "extra '# BEGIN SOLUTION' detected after QUESTION %s" % (last_qnum)
            elif qnum in solution:
                return "extra '# BEGIN SOLUTION' detected inside QUESTION %s" % (qnum)
            elif qnum in tests:
                return "'# BEGIN TESTS' appears before '# BEGIN SOLUTION' in QUESTION %s" % (qnum)
            solution.append(qnum)
            curr_solution = True
        elif '# END SOLUTION' in cell['source']:
            if qnum == None:
                if last_qnum == None:
                    return "exta '# END SOLUTION' detected before any '# BEGIN QUESTION'"
                else:
                    return "extra '# END SOLUTION' detected after QUESTION %s" % (last_qnum)
            elif qnum not in solution:
                return "'# END SOLUTION' detected before '# BEGIN SOLUTION' inside QUESTION %s" % (qnum)
            elif curr_solution == False:
                return "extra '# END SOLUTION' detected inside QUESTION %s" % (qnum)
            curr_solution = False
        elif '# BEGIN TESTS' in cell['source']:
            if qnum == None:
                if last_qnum == None:
                    return "exta '# BEGIN TESTS' detected before any '# BEGIN QUESTION'"
                else:
                    return "extra '# BEGIN TESTS' detected after QUESTION %s" % (last_qnum)
            elif qnum in tests:
                return "extra '# BEGIN TESTS' detected inside QUESTION %s" % (qnum)
            elif curr_test == True:
                return "'# BEGIN TESTS' appears before '# END SOLUTION' in QUESTION %s" % (qnum)
            tests.append(qnum)
            curr_test = True
        elif '# END TESTS' in cell['source']:
            if qnum == None:
                if last_qnum == None:
                    return "exta '# END TESTS' detected before any '# BEGIN QUESTION'"
                else:
                    return "extra '# END TESTS' detected after QUESTION %s" % (last_qnum)
            elif qnum not in tests:
                return "'# END TESTS' detected before '# BEGIN TESTS' inside QUESTION %s" % (qnum)
            elif curr_test == False:
                return "extra '# END TESTS' detected inside QUESTION %s" % (qnum)
            curr_test = False
        elif '# ASSIGNMENT CONFIG' not in cell['source']:
            return "malformed raw cell detected:\n%s" % (cell['source'])
    return True


def check_tests(FILE):
    '''check if the tests in FILE are in the correct format'''
    tests = extract_tests(FILE)
    for qnum in tests:
        public_test_detected = False
        for test_cell in tests[qnum]:
            if test_cell['cell_type'] != "markdown":
                continue
            try:
                test_details = parse_test_text(test_cell['source'])
            except Exception as e:
                return "error `%s` detected while trying to parse test in %s:\n%s" % (e, qnum, test_cell['source'])
            if test_details['test type'].lower().strip() not in ['public test', 'hidden test', 'dummy test']:
                return "unexpected test type detected in question %s; test type can only be 'Public Test', 'Hidden Test' or'Dummy Test'" % (qnum)
            if test_details['test type'] == "public test":
                if public_test_detected == False:
                    public_test_detected = True
                elif public_test_detected == True:
                    return "extra public test detected in %s:\n%s" % (qnum, test_cell['source'])
            if 'points' not in test_details:
                return "points not specified for test in %s:\n%s" % (qnum, test_cell['source'])
            if test_details['test type'] == "hidden test" and 'rubric item' not in test_details:
                return "rubric item not detected in question %s:\n%s" % (qnum, test_cell['source'])
            keys = set(test_details.keys()) - set(['test type'])
            accepted_public_keys = set(['points', 'format', 'answer', 'question'])
            if test_details['test type'] == 'public test' and len(keys -  accepted_public_keys) > 0:
                return "unexpected keys %s found in%s:\n%s" % ((keys -  accepted_public_keys), qnum, test_cell['source'])
            accepted_hidden_keys = set(['points', 'rubric item', 'reason for rubric', 'test notebook details', 'test dataset details'])
            if test_details['test type'] == 'hidden test' and len(keys -  accepted_hidden_keys) > 0:
                return "unexpected keys %s found in%s:\n%s" % ((keys -  accepted_hidden_keys), qnum, test_cell['source'])
    return True


def write_images(DIRECTORY):
    '''execute `gen_img.ipynb` file to generate images if the file exists in `TA_ONLY` directory'''
    img_file = os.path.join(DIRECTORY, 'TA_ONLY', 'gen_img.ipynb')
    if not os.path.exists(img_file):
        return
    with open(img_file, encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)
    ep = nbconvert.preprocessors.ExecutePreprocessor(timeout=300, kernel_name='python3')
    out = ep.preprocess(nb, {'metadata': {'path': os.path.dirname(img_file)}})


def write_tests(FILE, DIRECTORY, refresh=False):
    '''write import statement to the top of FILE and write all code test cells to FILE'''
    correct_points(FILE)
    nb = read_nb(FILE)
    new_tests = update_tests(FILE, refresh)
    new_nb_cells = []
    qnum = None
    test_cell = False
    for cell in nb['cells']:
        if cell['cell_type'] == "raw" and '# BEGIN QUESTION' in cell['source']:
            qnum = cell['source'].split('\n')[1].split(':')[1].strip()
        elif cell['cell_type'] == "raw" and '# END QUESTION' in cell['source']:
            qnum = None
        if qnum == None:
            new_nb_cells.append(cell)
            continue
        if cell['cell_type'] == "raw" and '# BEGIN TESTS' in cell['source']:
            new_nb_cells.append(cell)
            test_cell = True
            new_nb_cells.extend(new_tests[qnum])
        elif cell['cell_type'] == "raw" and '# END TESTS' in cell['source']:
            new_nb_cells.append(cell)
            test_cell = False
        elif test_cell == False:
            new_nb_cells.append(cell)
    if not (new_nb_cells[1]['cell_type'] == "code" and new_nb_cells[1]['source'] == 'import public_tests'):
        new_nb_cells.insert(1, new_code_cell('import public_tests'))
    nb['cells'] = new_nb_cells
    write_nb(nb, FILE)
    write_images(DIRECTORY)

def delete_tests(FILE):
    '''delete all code cells in the FILE that have references to `public_tests.py`'''
    nb = read_nb(FILE)
    new_cells = []
    for cell in nb['cells']:
        try:
            if cell['cell_type'] == "code":
                if "public_tests" in ast.unparse(ast.parse(cell['source'])):
                    continue
        except:
            pass
        if cell['cell_type'] == "markdown":
            if cell['source'].replace('#', '').strip().startswith('IGNORE'):
                continue
        new_cells.append(cell)
    nb['cells'] = new_cells
    write_nb(nb, FILE)

def get_qnums(FILE):
    '''return a list of all qnums in `FILE`'''
    qnums = []
    nb = read_nb(FILE)
    for cell in nb['cells']:
        if cell['cell_type'] == "raw" and '# BEGIN QUESTION' in cell['source']:
            qnum = cell['source'].split("name:")[1].split("\n")[0].strip()
            if qnum not in qnums:
                qnums.append(qnum)
    return qnums

def clean_text_swap_qnum(cells, qnum_1, qnum_2):
    '''replace instances of `qnum_1` in `cells` with `qnum_2`'''
    cells = copy.deepcopy(cells)
    if not (qnum_1[0] == "q" and qnum_1[1:].isdigit()):
        return cells
    if not (qnum_2[0] == "q" and qnum_2[1:].isdigit()):
        return cells
    for cell in cells:
        if cell['cell_type'] == "raw" and '# BEGIN QUESTION' in cell['source']:
            cell['source'] = cell['source'].replace(qnum_1, qnum_2)
        if cell['cell_type'] == "markdown":
            cell['source'] = cell['source'].replace(qnum_1, qnum_2)
            cell['source'] = cell['source'].replace("Question " + qnum_1[1:], "Question " + qnum_2[1:])
    return cells

def get_qnum_cells(nb, qnum):
    '''return the cells in `nb` corresponding to `qnum`'''
    new_cells = []
    qnum_found = False
    for cell in nb['cells']:
        if cell['cell_type'] == "raw" and '# BEGIN QUESTION' in cell['source']:
            curr_qnum = cell['source'].split("name:")[1].split("\n")[0].strip()
            if curr_qnum == qnum:
                qnum_found = True
            else:
                qnum_found = False
        if qnum_found:
            new_cells.append(cell)
    return new_cells

def swap_qnum(FILE, qnum_1, qnum_2):
    '''swap the locations of consecutive questions/functions/data structures `qnum_1` and `qnum_2` in `FILE`'''
    nb = read_nb(FILE)
    qnum_cells = {qnum_1: get_qnum_cells(nb, qnum_1), qnum_2: get_qnum_cells(nb, qnum_2)}
    
    new_cells = []
    qnum_found = False
    for cell in nb['cells']:
        if cell['cell_type'] == "raw" and '# BEGIN QUESTION' in cell['source']:
            curr_qnum = cell['source'].split("name:")[1].split("\n")[0].strip()
            if curr_qnum in qnum_cells:
                other_qnum = [qnum for qnum in qnum_cells if qnum != curr_qnum][0]
                new_cells.extend(clean_text_swap_qnum(qnum_cells[other_qnum], other_qnum, curr_qnum))
                qnum_found = True
            else:
                qnum_found = False
        if not qnum_found:
            new_cells.append(cell)
    nb['cells'] = new_cells
    write_nb(nb, FILE)

def find_additional_references(FILE, qnum):
    '''find any references to `qnum` that appear in `FILE` in addition to the question itself'''
    if not (qnum[0] == "q" and qnum[1:].isdigit()):
        return []
    additional_references = set()
    nb = read_nb(FILE)
    curr_qnum = None
    for cell in nb['cells']:
        if cell['cell_type'] == "raw" and '# BEGIN QUESTION' in cell['source']:
            curr_qnum = cell['source'].split("name:")[1].split("\n")[0].strip()
        if not cell['cell_type'] == "markdown":
            continue
        curr_text = cell['source']
        if curr_text.strip().startswith("**Question"):
            curr_text = curr_text[10:]
        if qnum in curr_text or 'Question ' + qnum[1:] in curr_text:
            additional_references.add(curr_qnum)
    return list(additional_references)
        

def rename_rubric(FILE, old_rubric_item, new_rubric_item):
    '''rename the rubric `old_rubric_item` to `new_rubric_item` in `FILE`'''
    nb = read_nb(FILE)
    qnum = old_rubric_item.split(":")[0].strip()
    old_name = old_rubric_item.split(":")[1].strip()
    new_name = new_rubric_item.split(":")[1].strip()
    qnum_found = False
    for cell in nb['cells']:
        if cell['cell_type'] == "raw" and '# BEGIN QUESTION' in cell['source']:
            new_qnum = cell['source'].split("name:")[1].split("\n")[0].strip()
            if new_qnum == qnum:
                qnum_found = True
        elif cell['cell_type'] == "raw" and '# END QUESTION' in cell['source']:
            qnum_found = False
        if not qnum_found:
            continue
        if not (cell['cell_type'] == "markdown" and "#### Hidden Test" in cell['source']):
            if not (cell['cell_type'] == "code" and "public_tests.rubric_check" in cell['source']):
                continue
        cell['source'] = cell['source'].replace(old_name, new_name)
    write_nb(nb, FILE)

def create_answers(FILE, ANSWERS):
    '''create `answers.json` at ANSWERS using the markdown test cells in FILE'''
    answers = {}
    tests = extract_tests(FILE)
    for qnum in tests:
        for test_cell in tests[qnum]:
            if test_cell['cell_type'] != "markdown":
                continue
            test_details = parse_test_text(test_cell['source'])
            if test_details['test type'] != "public test":
                continue
            if "answer" not in test_details:
                continue
            question = {"format": test_details['format'], "answer": test_details['answer']}
            if 'question' in test_details:
                question['question'] = test_details['question']
            answers[qnum] = question
    f = open(ANSWERS, 'w', encoding='utf-8')
    json.dump(answers, f, indent=2)
    f.close()


project_rubric_start_text = """
## Code reviews

- The Gradescope autograder will make deductions based on the rubric provided below.
- To ensure that you don't lose any points, you must **review** the rubric and make sure that you have followed the instructions provided in the project correctly.
- If you **fail** the **public tests** for a function or **hardcode** the answers to that question, you will automatically lose **all** points for that question.

## Rubric
"""

lab_rubric_start_text = """
## Code reviews

- The Gradescope autograder will make deductions based on the rubric provided below.
- You will receive full points if you pass the public tests associated with each question, and you will not receive any points for a question if you fail the public tests of that question.

## Rubric
"""


def get_public_test_points(FILE):
    '''identify how many points are allotted to each question, function, or data structure in FILE'''
    tests = extract_tests(FILE)
    points = {}
    for qnum in tests:
        for test_cell in tests[qnum]:
            if test_cell['cell_type'] != "markdown":
                continue
            test_details = parse_test_text(test_cell['source'])
            if test_details['test type'] != "public test":
                continue
            points[qnum] = test_details['points']
    return points


def get_rubric_text(test_cells):
    '''given some `test_cells` for a particular question, identify the rubric items in markdown test cells,
    and return processed text that can be written into RUBRIC file'''
    test_text = ""
    for test_cell in test_cells:
        if test_cell['cell_type'] != "markdown":
            continue
        test_details = parse_test_text(test_cell['source'])
        if test_details['test type'] != "hidden test":
            continue
        test_text += "\t- %s (-%g)\n" % (test_details['rubric item'], test_details['points'])
    test_text = test_text.strip("\n")
    return test_text


def create_rubric(FILE, RUBRIC):
    '''create `rubric.md` at RUBRIC using the markdown test cells in FILE'''
    title = os.path.basename(FILE).split(".")[0]
    if title.lower().startswith("p"):
        project_number = title.replace(" ", "").lower().replace('p', '')
        rubric_header = '# Project %s (P%s) Grading Rubric\n\n' % (project_number, project_number)
        rubric_header += project_rubric_start_text + "\n"
    elif title.lower().startswith("lab"):
        lab_number = title.replace(" ", "").lower().replace('lab-p', '')
        rubric_header = '# Lab Project %s (Lab-P%s) Grading Rubric\n\n' % (lab_number, lab_number)
        rubric_header += lab_rubric_start_text + "\n"
    tests = extract_tests(FILE)
    public_test_points = get_public_test_points(FILE)
    if sum(list(public_test_points.values())) == 0:
        return
    rubric_general = ""
    if 'general_deductions' in tests:
        rubric_general += get_rubric_text(tests['general_deductions']).replace("\t", "") + "\n\n"
    rubric_main = ""
    for qnum in tests:
        if qnum in ['general_deductions', 'summary']:
            continue
        qnum_rubric_text = get_rubric_text(tests[qnum])
        if qnum_rubric_text == "" and qnum not in public_test_points:
            continue
        qnum_name = qnum
        if not (qnum_name[0] == 'q' and qnum_name[1:].isdigit()):
            qnum_name = '`%s`' % (qnum_name)
        rubric_main += "- %s (%g)\n" % (qnum_name, public_test_points[qnum])
        if qnum_rubric_text != "":
            rubric_main += qnum_rubric_text + "\n\n"
        else:
            rubric_main += "\n"
    if rubric_general == "" and rubric_main == "":
        return
    rubric = rubric_header
    if rubric_general != "":
        rubric += "### General guidelines:\n\n" + rubric_general
    if rubric_main != "":
        rubric += "### Question specific guidelines:\n\n" + rubric_main
    f = open(RUBRIC, 'w', encoding='utf-8')
    f.write(rubric)
    f.close()