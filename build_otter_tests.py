import os, shutil, sys

def install_otter_tests():
    for path in sys.path:
        if path == os.getcwd():
            continue
        if os.path.isdir(os.path.join(path, 'otter_tests')):
            shutil.rmtree(os.path.join(path, 'otter_tests'))
    for path in sys.path:
        if path == os.getcwd():
            continue
        if os.path.isdir(path):
            print("otter_tests installed in %s" % (path))
            shutil.copytree('otter_tests', os.path.join(path, 'otter_tests'))
            break


install_otter_tests()

import otter_tests.write_test_code as write_test_code
import otter_tests.gen_public_tests as gen_public_tests
import otter_tests.gen_hidden_tests as gen_hidden_tests
import otter_tests.write_hidden_tests as write_hidden_tests
import otter_tests.build_project as build_project


def public_tests(FLAGS):
    nb_check = write_test_code.check_nb(FILE)
    tests_check = write_test_code.check_tests(FILE)
    if nb_check != True:
        print(nb_check)
        return
    if tests_check != True:
        print(tests_check)
        return

    if 'delete' in FLAGS:
        print("are you sure you want to delete all the references to `public_tests.py` in your notebook?")
        print("you must do this only if you are creating a new project from scratch")
        confirmation = input("if you press 'y', you will delete all references to `public_tests.py` [y/n]: ")
        if confirmation.lower() != 'y':
            return
        write_test_code.delete_tests(FILE)
        print("test code in %s deleted" % (os.path.basename(FILE)))
        return

    refresh = False
    if 'refresh' in FLAGS:
        refresh = True
        print("test code in %s refreshed" % (os.path.basename(FILE)))

    debug = False
    if 'debug' in FLAGS:
        debug = True
        print("gen_public_tests.ipynb not deleted in %s for debugging" % (DIRECTORY))

    write_test_code.write_tests(FILE, DIRECTORY, refresh)
    if refresh:
        print("tests generated in %s" % (FILE))
    else:
        print("tests refreshed in %s" % (FILE))
    write_test_code.create_answers(FILE, ANSWERS)
    print("%s created" % (ANSWERS))
    write_test_code.create_rubric(FILE, RUBRIC)
    print("%s created" % (RUBRIC))
    gen_public_tests.gen_public_tests(FILE, debug)
    print("`public_tests.py` generated in %s" % (DIRECTORY))


def refresh_hidden_tests_py(FLAGS):
    gen_hidden_tests.create_hidden_tests_py(FILE, DIRECTORY)
    print("`hidden_tests.py` refreshed in %s" % (DIRECTORY))


def refresh_hidden_tests_ipynb(FLAGS):
    write_hidden_tests.refresh_hidden_tests_ipynb(FILE, TESTS)
    print("`hidden_tests.ipynb` refreshed in %s" % (DIRECTORY))


def refresh_hidden_tests_data(FLAGS):
    gen_hidden_tests.create_hidden_directory(FILE, DIRECTORY, RUBRIC)
    sandbox_directory = os.path.join(DIRECTORY, 'sandbox', 'autograder', 'hidden')
    for file in ['hidden_tests.py', 'hidden_tests.ipynb']:
        shutil.copy(os.path.join(sandbox_directory, file), os.path.join(DIRECTORY, "hidden", file))
    gen_hidden_tests.generate_sandbox(FILE, DIRECTORY)
    shutil.rmtree(os.path.join(DIRECTORY, "hidden"))
    print("data in `hidden` directory refreshed to original data in %s" % (DIRECTORY))
    print("hidden_tests.ipynb needs to be run to regenerate the hidden tests")

def refresh_hidden_tests_swap(qnum_1, qnum_2):
    write_test_code.swap_qnum(FILE, qnum_1, qnum_2)
    gen_hidden_tests.swap_qnum(DIRECTORY, qnum_1, qnum_2)

def get_qnum():
    qnums = write_test_code.get_qnums(FILE)
    qnum = None
    while qnum not in qnums:
        qnum = input("enter a question, function, or data structure: ").strip()
    return qnum

def refresh_hidden_tests_move(FLAGS):
    print("enter the questions, functions, or data structures you wish to move")
    qnum_1 = get_qnum()
    print("enter the location you wish to move %s to" % (qnum_1))
    qnum_2 = get_qnum()
    confirmation = input("if you press 'y', you will move %s to appear right before %s [y/n]: " % (qnum_1, qnum_2))
    if confirmation.lower() != 'y':
        return
        
    qnums = write_test_code.get_qnums(FILE)
    qnum_1_idx = qnums.index(qnum_1)
    qnum_2_idx = qnums.index(qnum_2)
    if qnum_1_idx < qnum_2_idx:
        qnum_swaps = qnums[qnum_1_idx:qnum_2_idx:1]
    else:
        qnum_swaps = qnums[qnum_1_idx:qnum_2_idx-1:-1]
    swap_src = 0
    swap_dst = 1
    while swap_dst < len(qnum_swaps):
        qnum_src = qnum_swaps[swap_src]
        qnum_dst = qnum_swaps[swap_dst]
        refresh_hidden_tests_swap(qnum_src, qnum_dst)
        if ((qnum_src[0] == "q" and qnum_src[1:].isdigit()) and (qnum_dst[0] == "q" and qnum_dst[1:].isdigit())):
            swap_src = swap_dst
        swap_dst += 1
    write_test_code.create_rubric(FILE, RUBRIC)
    write_test_code.create_rubric(FILE, os.path.join(DIRECTORY, 'sandbox', 'autograder', 'rubric.md'))
    write_test_code.write_tests(FILE, DIRECTORY, True)
    write_hidden_tests.refresh_hidden_tests_ipynb(FILE, TESTS)
    additional_references = {}
    for qnum in qnum_swaps:
        qnum_additional_references = write_test_code.find_additional_references(FILE, qnum)
        if qnum_additional_references != []:
            additional_references[qnum] = qnum_additional_references
    print("moved `%s` to above `%s`" % (qnum_1, qnum_2))
    if additional_references != {}:
        print("WARNING: there are additional references to swapped questions in the markdown text for the following questions:")
        for qnum in additional_references:
            for reference in additional_references[qnum]:
                print("\treference to (old) %s under %s" % (qnum, reference))
        print("make sure you update these references IMMEDIATELY - you may have to `-rename` some rubric items too")
    print("WARNING: remember to refresh the public tests after all questions are moved")

def get_rubric_item():
    rubric = write_hidden_tests.get_rubric(FILE)
    rubric_item = input("enter a rubric item (or substring): ").strip()
    while rubric_item not in rubric:
        possible_rubrics = []
        for item in rubric:
            if rubric_item.lower() in item.lower():
                possible_rubrics.append(item)
        if len(possible_rubrics) == 0:
            print("none of the rubric items in %s match your input string" % (os.path.basename(FILE)))
            rubric_item = input("enter a rubric item (or substring): ").strip()
        else:
            print('here are the rubric items in %s that match your input string:' % (os.path.basename(FILE)))
            for i, item in enumerate(possible_rubrics):
                print('%d -> %s' % (i+1, item))
            multi_choice_input = input("enter a rubric item (or substring) or the number of the rubric item: ").strip()
            if multi_choice_input.isdigit() and 1 <= int(multi_choice_input) <= len(possible_rubrics):
                rubric_item = possible_rubrics[int(multi_choice_input) - 1]
            elif multi_choice_input in rubric:
                rubric_item = multi_choice_input
            else:
                print("that was not a valid option")
                rubric_item = input("enter a rubric item (or substring): ").strip()
    return rubric_item

def refresh_hidden_tests_rename(FLAGS):
    old_rubric_item = get_rubric_item()
    print("are you sure you want to rename the rubric item `%s`?" % (old_rubric_item))
    confirmation = input("if you press 'y', you can rename this rubric item [y/n]: ")
    if confirmation.lower() != 'y':
        return
    qnum = old_rubric_item.split(":")[0].strip()
    confirmation = "n"
    while confirmation.lower() != "y":
        new_rubric_item = input("enter the new name for this rubric item (without the qnum at the start): ")
        while ":" in new_rubric_item:
            print("unexpected character ':' found in the name, you should not enter the qnum here")
            new_rubric_item = input("enter the new name for this rubric item (without the qnum at the start): ")
        new_rubric_item = qnum + ": " + new_rubric_item.strip()
        print("are you sure you want to rename the rubric item to `%s`?" % (new_rubric_item))
        confirmation = input("press 'y' to rename, press 'n' to enter a different name [y/n]: ")
        if confirmation.lower() not in ["y", "n"]:
            return
    gen_hidden_tests.rename_rubric(DIRECTORY, old_rubric_item, new_rubric_item)
    write_test_code.rename_rubric(FILE, old_rubric_item, new_rubric_item)
    write_test_code.create_rubric(FILE, RUBRIC)
    write_test_code.create_rubric(FILE, os.path.join(DIRECTORY, 'sandbox', 'autograder', 'rubric.md'))
    print("renamed `%s` to `%s`" % (old_rubric_item, new_rubric_item))
    
def refresh_hidden_tests(FLAGS):
    refresh_flags = list(FLAGS.intersection(set(['py', 'ipynb', 'data', 'move', 'rename', 'all'])))
    if len(refresh_flags) != 1:
        print("you must pass a flag '-py', '-ipynb', '-data', or '-all'")
        print("'-py' will refresh only the `hidden_tests.py` file")
        print("'-ipynb' will refresh only the `hidden_tests.ipynb` file")
        print("'-data' will refresh only the data files")
        print("'-move' will change the numbering of questions")
        print("'-rename' will rename a rubric item")
        print("'-all' will refresh everything")
        return
    flag = refresh_flags[0]
    if flag == "py":
        refresh_hidden_tests_py(FLAGS)
    elif flag == "ipynb":
        refresh_hidden_tests_ipynb(FLAGS)
    elif flag == "data":
        refresh_hidden_tests_data(FLAGS)
    elif flag == "move":
        refresh_hidden_tests_move(FLAGS)
    elif flag == "rename":
        refresh_hidden_tests_rename(FLAGS)
    elif flag == "all":
        refresh_hidden_tests_py(FLAGS)
        refresh_hidden_tests_ipynb(FLAGS)
        refresh_hidden_tests_data(FLAGS)


def write_hidden_tests_random(FLAGS):
    new_random_data = True
    tests = write_hidden_tests.read_nb(TESTS)
    for idx in range(len(tests['cells'])):
        cell = tests['cells'][idx]
        if cell['cell_type'] != 'markdown':
            continue
        if '## Random Data Generation' in cell['source']:
            break
    next_cell = tests['cells'][idx+1]
    if next_cell['cell_type'] == 'code' and 'def random_data' in next_cell['source']:
        new_random_data = False

    if new_random_data == False:
        print("are you sure you want to refresh `random_data`?")
        confirmation = input("if you press 'y', you will lose the function generated with GPT [y/n]: ")
        if confirmation.lower() != 'y':
            return
    write_hidden_tests.write_random_data(FILE, TESTS, ALL_REPLIES, True)
    print("`random_data` defined in `hidden_tests.ipynb`")


def write_hidden_tests_all(FLAGS):
    print("are you sure you want to generate all hidden tests at once? this could cost around $10 to process")
    print("it would be safer to generate the hidden tests one at a time and update the test details if necessary")
    confirmation = input("if you press 'y', you will generate all hidden tests with GPT [y/n]: ")
    if confirmation.lower() != 'y':
        return
    write_hidden_tests.write_hidden_tests(FILE, TESTS, ALL_REPLIES)
    print("all hidden tests written in `hidden_tests.ipynb`")


def write_hidden_tests_redo(FLAGS):
    rubric_item = rubric_item = get_rubric_item()
    print("are you sure you want to regenerate the tests for `%s`?" % (rubric_item))
    confirmation = input("if you press 'y', you will lose the hidden test generated with GPT [y/n]: ")
    if confirmation.lower() != 'y':
        return
    write_rubric_test(FILE, TESTS, ALL_REPLIES, rubric_item, True)
    print("hidden test regenerated for `%s`" % (rubric_item))


def clean_hidden_tests_ipynb(FLAGS):
    print("are you sure you want to clean `hidden_tests.ipynb`?")
    confirmation = input("if you press 'y', you will lose all the hidden tests generated with GPT [y/n]: ")
    if confirmation.lower() != 'y':
        return

    sandbox_file = os.path.join(DIRECTORY, 'sandbox', 'autograder', 'hidden', 'hidden_tests.ipynb')
    if not os.path.isdir(os.path.join(DIRECTORY, 'old_hidden_tests')):
        os.mkdir(os.path.join(DIRECTORY, 'old_hidden_tests'))
    num_old_files = len(os.listdir(os.path.join(DIRECTORY, 'old_hidden_tests')))
    shutil.copy(sandbox_file, os.path.join(DIRECTORY, 'old_hidden_tests', 'hidden_tests_%d.ipynb' % (num_old_files)))
    print("copy of the old `hidden_tests.ipynb` stored in %s" % (os.path.join(DIRECTORY, 'old_hidden_tests')))

    gen_hidden_tests.create_hidden_tests_ipynb(FILE, DIRECTORY)
    write_hidden_tests.write_base_hidden_tests(FILE, TESTS)
    print("clean copy of `hidden_tests.ipynb` generated in %s" % (DIRECTORY))


def write_hidden_ipynb_tests(FLAGS):
    write_flags = list(FLAGS.intersection(set(['clean', 'random', 'next', 'all', 'redo'])))
    if len(write_flags) != 1:
        print("you must pass a flag '-clean', '-random', '-next', '-all', or '-redo'")
        print("'-clean' will delete all existing tests and create a clean copy of `hidden_tests.ipynb`")
        print("'-random' will use GPT to update the function `random_data` used for generating new random datasets")
        print("'-next' will use GPT to update only the next empty hidden test")
        print("'-all' will use GPT to update all the empty hidden test")
        print("'-redo' will use GPT to regenerate code for an already written hidden test")
        return
    flag = write_flags[0]
    if flag == "clean":
        clean_hidden_tests_ipynb(FLAGS)
    elif flag == "random":
        write_hidden_tests_random(FLAGS)
    elif flag == "next":
        rubric_written = write_hidden_tests.write_latest_rubric_test(FILE, TESTS, ALL_REPLIES)
        if rubric_written == False:
            print("no more hidden tests left to write; use the -redo flag to regenerate code for already written tests")
            return
        print("hidden test written for `%s`" % (rubric_written))
    elif flag == "all":
        write_hidden_tests_all(FLAGS)
    elif flag == "redo":
        write_hidden_tests_redo(FLAGS)


def hidden_tests(FLAGS):
    if not (os.path.isfile(RUBRIC) and os.path.isfile(ANSWERS)):
        public_tests(FLAGS - set(['refresh', 'debug']))

    refresh = False
    if 'refresh' in FLAGS:
        refresh = True

    write = False
    if 'write' in FLAGS:
        write = True

    if not os.path.exists(os.path.join(DIRECTORY, "sandbox")):
        gen_hidden_tests.gen_hidden_tests(FILE, DIRECTORY, RUBRIC)
        write_hidden_tests.write_base_hidden_tests(FILE, TESTS)
        return

    if not (refresh or write):
        print("hidden tests already exist")
        print("pass the flag '-refresh' if you wish to refresh the hidden tests")
        print("pass the flag '-write' if you wish to write hidden tests to `hidden_tests.ipynb`")
        return

    if refresh:
        print("before generating hidden tests, you need to ensure that none of the files in the `sandbox` directory are open")
        print("if any files are open in Jupyter or elsewhere, this process will FAIL and you will lose ALL your data")
        confirmation = input("press 'y' to confirm that no files in the `sandbox` directory are open [y/n]: ")
        if confirmation.lower() != 'y':
            return
        refresh_hidden_tests(FLAGS)
    elif write:
        write_hidden_ipynb_tests(FLAGS)


def otter_tests():
    global args, FLAGS, DIRECTORY, FILE, ANSWERS, RUBRIC, TESTS, ALL_REPLIES

    args = sys.argv[1:]
    if len(args) == 0:
        print("you must pass the directory of the project as an argument")
        return
    FLAGS = set([flag[1:] for flag in args[1:] if flag.startswith("-")])

    DIRECTORY = args[0].lower()
    FILE = os.path.join(DIRECTORY, os.path.basename(DIRECTORY)+".ipynb")
    ANSWERS = os.path.join(DIRECTORY, 'answers.json')
    RUBRIC = os.path.join(DIRECTORY, 'rubric.md')
    TESTS = os.path.join(DIRECTORY, 'sandbox', 'autograder', 'hidden', 'hidden_tests.ipynb')
    ALL_REPLIES = os.path.join(DIRECTORY, 'sandbox', 'autograder', 'all_replies.txt')

    if not os.path.isdir(DIRECTORY):
        print("your first argument must be the directory of a project such as 'p2', 'lab-p3', or 'p13'")
        return

    gen_flags = list(FLAGS.intersection(set(['public', 'hidden', 'build'])))
    if len(gen_flags) != 1:
        print("you must pass a flag '-public', '-hidden', or '-build'")
        print("'-public' will generate or refresh only the public tests")
        print("'-hidden' will generate or refresh the hidden tests too")
        print("'-build' will build the final student and autograder versions of the project")
        return
    flag = gen_flags[0]
    if flag == 'public':
        public_tests(FLAGS)
    elif flag == 'hidden':
        hidden_tests(FLAGS)
    elif flag == 'build':
        build_project.build_project(FILE, DIRECTORY)
        print("project built at %s" % (DIRECTORY))


otter_tests()
