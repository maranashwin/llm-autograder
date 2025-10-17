### Otter Tests Toolkit

This folder contains helper scripts, templates, and assets used to generate, write, and package Otter Grader tests for projects/labs. These modules are orchestrated by higher-level build scripts (for example, `build_otter_tests.py` at the repo root) to produce student and autograder deliverables.

### What's in here

- **`gen_public_tests.py`**: Programmatically generates `public_tests.py` from a project notebook and `answers.json`.
  - Rewrites the notebook to capture expected answers, namedtuple definitions, plots, and DataFrames, then emits a clean `public_tests.py`.


- **`gen_hidden_tests.py`**: Creates the scaffolding for hidden tests from a source notebook and rubric.
  - Parses the rubric to build `hidden/` subdirectories per rubric item and writes per-item `README.txt` markers.
  - Generates `hidden_tests.py` from the template notebook based on selected tags and writes a base `hidden_tests.ipynb`.
  - Produces a `sandbox/` notebook copy where calls to `grader.check` reset hidden tests to ease iterative development.


- **`write_hidden_tests.py`**: Builds out the main hidden test authoring notebook.
  - Extracts required functions/data structures and their dependencies from the source notebook and injects them (self-contained) into `hidden_tests.ipynb`.
  - Uses large language models (behind your API key) to draft dataset modifications, notebook modifications, and per-rubric feedback snippets.


- **`write_test_code.py`**: Parses test cells in a project/staff notebook and writes runnable code tests inline.


- **`build_project.py`**: Executes Otter Assign on a project notebook to produce `student/` and `autograder/` outputs, then post-processes them.
  - Executes the notebook, runs `otter assign`, injects/save/export cells, and writes `environment.yml` and `setup.sh` into the autograder zip.


- **`templates/`**: Starter assets used by the generators.
  - `hidden_tests_template.ipynb`: Base notebook skeleton for hidden tests before rubric-specific content is added.
  - `hidden_tests.ipynb`: A reference hidden tests notebook used to extract tagged code into `hidden_tests.py`.
  - `public_tests_template.py`: Canonical `public_tests.py` template populated by `gen_public_tests.py`.
