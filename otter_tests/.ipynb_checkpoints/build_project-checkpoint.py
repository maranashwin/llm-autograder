import os, json, copy, nbformat, nbconvert, ast, shutil, subprocess, sys, zipfile, otter.version, datetime
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


def clean_hidden_directories(directory):
    '''delete all files other than `necessary_files` from all subdirectories in `directory`'''
    for item in os.listdir(directory):
        path = os.path.join(directory, item)
        if os.path.isdir(path):
            if item in ["images"]:
                shutil.rmtree(path)
            else:
                clean_hidden_directories(path)
        elif os.path.isfile(path):
            if item.startswith("hidden_tests"):
                continue
            if item.endswith(".ipynb") or item.endswith(".md"):
                os.remove(path)


submission_instructions = """## Submission
It is recommended that at this stage, you Restart and Run all Cells in your notebook.
That will automatically save your work and generate a zip file for you to submit.

**SUBMISSION INSTRUCTIONS**:
1. **Upload** the zipfile to Gradescope.
2. If you completed the project with a **partner**, make sure to **add their name** by clicking "Add Group Member"
in Gradescope when uploading the zip file.
3. Check **Gradescope** results as soon as the auto-grader execution gets completed.
4. Your **final score** for this project is the score that you see on **Gradescope**.
5. You are **allowed** to resubmit on Gradescope as many times as you want to.
6. **Contact** a TA/PM if you lose any points on Gradescope for any **unclear reasons**."""

save_content = """# running this cell will create a new save checkpoint for your notebook
from IPython.display import display, Javascript
display(Javascript('IPython.notebook.save_checkpoint();'))"""


def modify_project_nb(file, lab_file=False):
    '''modifies cells and adds in code to save file and check file size to the student and autograder notebooks'''
    nb_name = os.path.basename(file).split(".")[0]
    nb = read_nb(file)

    # the `import otter` cell
    first_cell_content = "# import and initialize otter\n"
    first_cell_content += "import otter\n"
    first_cell_content += "grader = otter.Notebook(\"%s.ipynb\")" % (nb_name)
    nb['cells'][0]["source"] = first_cell_content
    nb['cells'][0]["metadata"]["cell_type"] = "code"

    # make all markdown cells with no attached images and code cells marked uneditable, both uneditable and undeleteable
    for cell in nb["cells"]:
        if cell["cell_type"] == "markdown" and "attachments" not in cell:
            cell["metadata"]["editable"] = False
            cell["metadata"]["deletable"] = False
        elif  cell["cell_type"] == "code" and '# DO NOT EDIT THIS CELL' in cell['source']:
            cell["metadata"]["editable"] = False
            cell["metadata"]["deletable"] = False
        elif cell['cell_type'] == "code" and cell['source'].startswith('grader.'):
            cell["metadata"]["editable"] = False
            cell["metadata"]["deletable"] = False
        elif cell['cell_type'] == "code" and "import otter" in cell['source']:
            cell["metadata"]["editable"] = False
            cell["metadata"]["deletable"] = False
        elif cell['cell_type'] == "code" and "import public_tests" in cell['source']:
            cell["metadata"]["editable"] = False
            cell["metadata"]["deletable"] = False
        else:
            cell["metadata"]["editable"] = True
            cell["metadata"]["deletable"] = True
            
    # the cell above the very last cell has the submission markdown text and needs to be replaced
    nb["cells"][-3]["source"] = submission_instructions
    nb["cells"][-3]["cell_type"] = "markdown"
    nb["cells"][-3]["metadata"]["editable"] = False
    nb["cells"][-3]["metadata"]["deletable"] = False
    
    # between the markdown text and the export call, we inject code to auto-save the notebook
    nb["cells"].insert(-2, new_code_cell(save_content))
    nb["cells"][-3]["metadata"]["cell_type"] = "code"
    nb["cells"][-3]["metadata"]["editable"] = False
    nb["cells"][-3]["metadata"]["deletable"] = False

    # do not edit any more cells if the file is for a lab project and does not have any hidden tests
    if lab_file:
        last_cell_content = "grader.export(pdf=False, run_tests=False)"
        nb['cells'][-2]["source"] = last_cell_content
        nb['cells'][-2]["cell_type"] = "code"
        nb["cells"][-2]["metadata"]["editable"] = False
        nb["cells"][-2]["metadata"]["deletable"] = False
        with open(file, "w", encoding='utf-8') as f:
            nbformat.write(nb, f)
        return

    # the very last cell is always an empty markdown cell, so the actual last cell is at index -2
    # with the `grader.export` call
    last_cell_content = "grader.export(pdf=False, run_tests=False, files=[\"%s.py\"])" % (nb_name)
    nb['cells'][-2]["source"] = last_cell_content
    nb['cells'][-2]["cell_type"] = "code"
    nb["cells"][-2]["metadata"]["editable"] = False
    nb["cells"][-2]["metadata"]["deletable"] = False

    # after the auto-save cell, we inject code to convert the notebook into a py file (for cheating detection)
    to_py_content = "!jupytext --to py " + nb_name + ".ipynb"
    nb["cells"].insert(-2, new_code_cell(to_py_content))
    nb["cells"][-3]["metadata"]["cell_type"] = "code"
    nb["cells"][-3]["metadata"]["editable"] = False
    nb["cells"][-3]["metadata"]["deletable"] = False

    with open(file, "w", encoding='utf-8') as f:
        nbformat.write(nb, f)


hidn_initialize_text = """
HIDDEN_FILE = os.path.join("hidden", "hidden_tests.py")
if os.path.exists(HIDDEN_FILE):
    import hidden.hidden_tests as hidn"""

new_hidn_functions = """
def rubric_check(rubric_point, check_past_errors=False):
    print('All test cases passed!')
    
def get_summary():
    print('Total Score: %d/%d' % (TOTAL_SCORE, TOTAL_SCORE))

def display_late_days_used():
    print()
"""


def modify_student_tests(tests_file):
    '''remove all references to the hidden tests in `public_tests.py` in the `student` directory'''
    f = open(tests_file, encoding='utf-8')
    py_data = f.read()
    f.close()
    
    py_data = py_data.replace(hidn_initialize_text.strip("\n "), "")
    py_data_start = py_data.find("def reset_hidden_tests()")
    py_data = py_data[:py_data_start] + new_hidn_functions.strip("\n ")
    
    f = open(tests_file, 'w', encoding='utf-8')
    f.write(py_data)
    f.close()


general_setup = """#!/usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive
apt-get clean
apt-get update
apt-get install -y wget pandoc texlive-xetex texlive-fonts-recommended texlive-plain-generic \
    build-essential libcurl4-gnutls-dev libxml2-dev libssl-dev libgit2-dev texlive-lang-chinese

# install mamba
if [ $(uname -p) = "arm" ] || [ $(uname -p) = "aarch64" ] ; \
    then wget -nv https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-aarch64.sh \
        -O /autograder/source/mamba_install.sh ; \
    else wget -nv https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh \
        -O /autograder/source/mamba_install.sh ; \
fi
chmod +x /autograder/source/mamba_install.sh
/autograder/source/mamba_install.sh -b
echo "export PATH=/root/mambaforge/bin:\$PATH" >> /root/.bashrc

export PATH=/root/mambaforge/bin:$PATH
export TAR="/bin/tar"

# install dependencies with mamba
mamba env create -f /autograder/source/environment.yml

# set mamba shell
mamba init --all"""

plots_setup = """#!/usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive
apt-get clean
apt-get update
apt-get install -y wget pandoc texlive-xetex texlive-fonts-recommended texlive-plain-generic \
    build-essential libcurl4-gnutls-dev libxml2-dev libssl-dev libgit2-dev texlive-lang-chinese \
    git cmake pkg-config libtiff5-dev libjpeg-dev zlib1g-dev libicu-dev libpango1.0-dev \
    libcairo2-dev autoconf automake libtool libleptonica-dev libgif7 libwebpmux3
git clone https://github.com/tesseract-ocr/tesseract.git
cd tesseract
./autogen.sh
./configure
make
make install
ldconfig
apt-get install -y tesseract-ocr
wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata
mv -v eng.traineddata /usr/local/share/tessdata/

# install mamba
if [ $(uname -p) = "arm" ] || [ $(uname -p) = "aarch64" ] ; \
    then wget -nv https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-aarch64.sh \
        -O /autograder/source/mamba_install.sh ; \
    else wget -nv https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh \
        -O /autograder/source/mamba_install.sh ; \
fi
chmod +x /autograder/source/mamba_install.sh
/autograder/source/mamba_install.sh -b
echo "export PATH=/root/mambaforge/bin:\$PATH" >> /root/.bashrc

export PATH=/root/mambaforge/bin:$PATH
export TAR="/bin/tar"

# install dependencies with mamba
mamba env create -f /autograder/source/environment.yml

# set mamba shell
mamba init --all"""

general_environment = """name: otter-env
channels:
  - defaults
  - conda-forge
dependencies:
  - python=%s
  - pip
  - nb_conda_kernels
  - pip:
      - datascience
      - jupyter_client
      - ipykernel
      - matplotlib
      - pandas==1.5.3
      - ipywidgets
      - scipy
      - seaborn
      - scikit-learn
      - jinja2
      - nbconvert
      - nbformat
      - dill
      - numpy
      - pymongo
      - pypdf
      - otter-grader==%s
""" % (".".join(map(str, sys.version_info[:3])), otter.version.__version__)

plots_environment = """name: otter-env
channels:
  - defaults
  - conda-forge
dependencies:
  - python=%s
  - pip
  - nb_conda_kernels
  - pip:
      - datascience
      - jupyter_client
      - ipykernel
      - matplotlib
      - pandas==1.5.3
      - ipywidgets
      - scipy
      - seaborn
      - scikit-learn
      - jinja2
      - nbconvert
      - nbformat
      - dill
      - numpy
      - pymongo
      - pypdf
      - pytesseract
      - otter-grader==%s
""" % (".".join(map(str, sys.version_info[:3])), otter.version.__version__)


def unzip(zip_file):
    '''unzips a zip file'''
    with zipfile.ZipFile(zip_file, 'r') as zip_data:
        zip_data.extractall(zip_file.split(".")[0])


def rezip(directory):
    '''zips a directory'''
    rootlen = len(directory) + 1
    with zipfile.ZipFile(directory + '.zip', 'w', zipfile.ZIP_DEFLATED) as zip_data:
        for base, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(base, file)
                zip_data.write(file_path, file_path[rootlen:])


def build_project(FILE, DIRECTORY, destination="project"):
    '''this function builds the autograder using the `<project>.ipynb` `file` at `destination`'''
    filename = os.path.basename(FILE).split(".")[0]
    lab_file = False
    if filename.startswith("lab"):
        lab_file = True
        
    if os.path.exists(os.path.join(DIRECTORY, "hidden")):
        shutil.rmtree(os.path.join(DIRECTORY, "hidden"))
    if os.path.exists(os.path.join(DIRECTORY, "sandbox", "autograder", "hidden")):
        shutil.copytree(os.path.join(DIRECTORY, "sandbox", "autograder", "hidden"), os.path.join(DIRECTORY, "hidden"))
        clean_hidden_directories(os.path.join(DIRECTORY, "hidden"))
    
    run_otter_tests(FILE, DIRECTORY, destination)
    if os.path.exists(os.path.join(DIRECTORY, "hidden")):
        shutil.rmtree(os.path.join(DIRECTORY, "hidden"))

    modify_project_nb(os.path.join(DIRECTORY, destination, "autograder", os.path.basename(FILE)), lab_file)
    modify_project_nb(os.path.join(DIRECTORY, destination, "student", os.path.basename(FILE)), lab_file)
    modify_student_tests(os.path.join(DIRECTORY, destination, "student", "public_tests.py"))

    for zip_file in os.listdir(os.path.join(DIRECTORY, destination, "autograder")):
        if zip_file.endswith(".zip"):
            zip_path = os.path.join(DIRECTORY, destination, "autograder", zip_file)
            break
    unzip(zip_path)
    zip_directory = zip_path.split(".")[0]

    f = open(os.path.join(zip_directory, 'environment.yml'), "w", encoding='utf-8')
    if filename in ["p9", "p11", "p13"]:
        f.write(plots_environment)
    else:
        f.write(general_environment)
    f.close()

    f = open(os.path.join(zip_directory, 'setup.sh'), "w", encoding='utf-8')
    if filename in ["p9", "p11", "p13"]:
        f.write(plots_setup)
    else:
        f.write(general_setup)
    f.close()

    rezip(zip_directory)
    shutil.rmtree(zip_directory)
