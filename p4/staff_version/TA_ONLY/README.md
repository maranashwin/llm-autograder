### Dataset Update Instructions:

1. Open Jupyter and open `p4\gen_csv.ipynb`.
2. If a new *Pokemon generation* is released, update the variable `regions` in
Cell 6 of the notebook.
3. Execute the notebook (fix any bugs as they appear).
4. The notebook will update `pokemon_stats.csv` and `type_effectiveness_stats.csv`.

## Refresh Instructions:

1. First open Jupyter and open `p4\p4.ipynb`.
2. Update all references to the previous semester's repository. Fix all links.
3. Make any necessary changes to the questions and solutions.
**Follow the Guidelines listed below for refreshing questions.**
4. Restart and Rerun all Cells, and save the notebook.
Run the file `p4\TA_ONLY\gen_img.ipynb` to update the image in the notebook.
5. Go back and edit the questions to change the number of unique Pokemon
that appear in the dataset, if the number of Pokemon is not neatly divisible.
Repeat the last two steps.
6. Update the names of the variables used to store the answers in `p4\answers.json`.
7. Make any necessary changes to `p4\rubric.md`.
8. Run `python -c "import otter_tests.gen_tests; otter_tests.gen_tests.refresh_project('p4\p4.ipynb')"`
(from the repo directory).
9. With Jupyter, open `p4\sandbox\autograder\hidden\hidden_tests.ipynb`.
10. Update the hidden tests (especially for the refreshed questions).
11. Execute `p4\sandbox\autograder\hidden\hidden_tests.ipynb`.
12. Run `python -c "import otter_tests.gen_tests; otter_tests.gen_tests.build_otter_files('p4\p4.ipynb')"`
(from the repo directory).
13. Extensively test the hidden tests for each question.
14. Copy over all files/folders in the `p4\otter_files\student` directory to the
public repository.
15. Additionally, copy/paste the `p4\gen_csv.ipynb` file to the public repository.

### Guidelines for refreshing questions:

This project is about testing conditional statements. So, we have students create functions with conditional statements. **We need to check that all branches of the decision tree work**. For example, if the students' code is expected to look like this:
```python
if <condition-1>:
    <statement-1>
else:
    <statement-2>
```

then, we need to create one question such that `<condition-1>` is `True` and one where it is `False`. Otherwise, we cannot be sure that their function actually works as it should. This principle **must** be followed especially for some of the more complicated functions such as `battle` which has a lot of branching.

As an example, for the first two questions of the project (where the `damage` function is being tested), we want the **first question** to be framed such that the `attacker` chooses its *Physical* attack, and the **second question** to be framed such that the `attacker` chooses its *Special* attack.
