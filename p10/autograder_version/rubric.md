# Project 10 (P10) Grading Rubric


## Code reviews

- The Gradescope autograder will make deductions based on the rubric provided below.
- To ensure that you don't lose any points, you must **review** the rubric and make sure that you have followed the instructions provided in the project correctly.
- If you **fail** the **public tests** for a function or **hardcode** the answers to that question, you will automatically lose **all** points for that question.

## Rubric

### General guidelines:

- Outputs not visible/did not save the notebook file prior to running the cell containing "export". We cannot see your output if you do not save before generating the zip file. (-3)
- Used concepts/modules such as csv.DictReader and pandas not covered in class yet. Note that built-in functions that you have been introduced to can be used. (-3)
- Used bare try/except blocks without explicitly specifying the type of exceptions that need to be caught (-3)
- Large outputs such as stars_dict or planets_list are displayed in the notebook. (-3)
- Import statements are not mentioned in the required cell at the top of the notebook. (-1)

### Question specific guidelines:

- q1 (3)
	- answer is not sorted explicitly (-2)
	- answer does not remove all files and directories that start with `.` (-1)

- q2 (3)
	- recomputed variable defined in Question 1, or the answer is not sorted explicitly (-1)
	- answer does not remove all files and directories that start with `.` (-1)
	- paths are hardcoded using slashes (-1)

- q3 (4)
	- recomputed variable defined in Question 1 or Question 2, or the answer is not sorted explicitly (-1)
	- answer does not remove all files and directories that start with `.` (-1)
	- answer does not check only for files that end with `.csv` (-1)
	- paths are hardcoded using slashes (-1)

- q4 (4)
	- recomputed variable defined in Question 1 or Question 2, or the answer is not sorted explicitly (-1)
	- answer does not remove all files and directories that start with `.` (-1)
	- answer does not check for only files that start with `stars` (-1)
	- paths are hardcoded using slashes (-1)

- `Star` (2)
	- data structure is defined more than once (-1)
	- data structure is defined incorrectly (-1)

- `star_cell` (4)
	- function does not typecast values based on columns (-1)
	- column indices are hardcoded instead of using column names (-1)
	- function logic is incorrect (-1)
	- function is defined more than once (-1)

- q5 (4)
	- `star_cell` function is not used to answer (-1)
	- answer unnecessarily iterates over the entire dataset (-1)
	- paths are hardcoded using slashes (-1)

- `get_stars` (6)
	- function logic is incorrect (-2)
	- hardcoded the name of directory inside the function instead of passing it as a part of the input argument (-1)
	- function is called more than twice with the same dataset (-1)
	- `star_cell` function is not used (-1)
	- function is defined more than once (-1)

- q6 (2)
	- `stars_1_dict` data structure is not used to answer (-1)
	- paths are hardcoded using slashes (-1)

- q7 (3)
	- incorrect logic is used to answer (-1)
	- `stars_1_dict` data structure is not used to answer (-1)

- q8 (3)
	- incorrect logic is used to answer (-1)
	- `get_stars` function is not used to answer (-1)
	- paths are hardcoded using slashes (-1)

- `stars_dict` (3)
	- data structure is defined incorrectly (-1)
	- `get_stars` function is not used (-1)
	- `stars_paths` is not used to find paths of necessary files (-1)

- q9 (2)
	- `stars_dict` data structure is not used to answer (-2)

- q10 (3)
	- incorrect logic is used to answer (-1)
	- `stars_dict` data structure is not used to answer (-1)

- q11 (3)
	- answer does not check for only stars that start with `Kepler` (-1)
	- incorrect logic is used to answer (-1)
	- `stars_dict` data structure is not used to answer (-1)

- `Planet` (2)
	- data structure is defined more than once (-1)
	- data structure is defined incorrectly (-1)

- `planet_cell` (5)
	- function does not typecast values based on columns (-1)
	- column indices are hardcoded instead of using column names (-1)
	- boolean values are not typecasted correctly (-1)
	- function logic is incorrect (-1)
	- function is defined more than once (-1)

- q12 (4)
	- `planet_cell` function is not used to answer (-1)
	- `mapping_1_json` data structure is not used to answer (-1)
	- answer unnecessarily iterates over the entire dataset (-1)
	- paths are hardcoded using slashes (-1)

- `get_planets` (8)
	- function logic is incorrect (-2)
	- hardcoded the name of directory inside the function instead of passing it as a part of the input argument (-1)
	- function is called more than twice with the same dataset (-1)
	- `planet_cell` function is not used (-1)
	- function is defined more than once (-3)

- q13 (3)
	- `get_planets` function is not used to answer (-1)
	- paths are hardcoded using slashes (-1)

- q14 (3)
	- incorrect logic is used to answer (-1)
	- `get_planets` function is not used to answer (-1)
	- paths are hardcoded using slashes (-1)

- q15 (3)
	- `get_planets` function is not used to answer (-1)
	- paths are hardcoded using slashes (-1)

- `planets_list` (4)
	- data structure is defined incorrectly (-2)
	- `get_planets` function is not used (-1)
	- paths are hardcoded using slashes (-1)

- q16 (2)
	- `planets_list` data structure is not used to answer (-2)

- q17 (3)
	- incorrect comparison operator is used (-1)
	- incorrect logic is used to answer (-1)
	- `planets_list` data structure is not used to answer (-1)

- q18 (4)
	- `planets_list` and `stars_dict` data structures are not used to answer (-2)
	- did not exit loop and instead iterated further after finding the answer (-1)

- q19 (5)
	- incorrect comparison operator is used (-1)
	- incorrect logic is used to answer (-1)
	- `planets_list` and `stars_dict` data structures are not used to answer (-2)

- q20 (5)
	- answer does not include all Planets that orbit the Star (-1)
	- incorrect logic is used to answer (-1)
	- `planets_list` and `stars_dict` data structures are not used to answer (-2)

