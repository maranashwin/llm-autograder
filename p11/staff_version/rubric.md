# Project 11 (P11) Grading Rubric


## Code reviews

- The Gradescope autograder will make deductions based on the rubric provided below.
- To ensure that you don't lose any points, you must **review** the rubric and make sure that you have followed the instructions provided in the project correctly.
- If you **fail** the **public tests** for a function or **hardcode** the answers to that question, you will automatically lose **all** points for that question.

## Rubric

### General guidelines:

- Outputs not visible/did not save the notebook file prior to running the cell containing "export". We cannot see your output if you do not save before generating the zip file. (-3)
- Used concepts/modules such as csv.DictReader, os.walk, and pandas not covered in class yet. Note that built-in functions that you have been introduced to can be used. (-3)
- Large outputs such as stars_dict or planets_list are displayed in the notebook. (-3)
- Import statements are not mentioned in the required cell at the top of the notebook. (-1)

### Question specific guidelines:

- q1 (3)
	- incorrect logic is used to answer (-1)
	- `planets_list` data structure is not used to answer (-1)

- q2 (3)
	- incorrect logic is used to answer (-1)
	- recomputed variable defined in Question 1 (-1)

- q3 (3)
	- incorrect logic is used to answer (-1)
	- recomputed variable defined in Question 1 (-1)
	- `stars_dict` data structure is not used to answer (-1)

- q4 (5)
	- incorrect logic is used to answer (-1)
	- `planets_list` data structure is not used to answer (-1)
	- plot is incorrect (-1)
	- plot is not properly labeled (-1)

- q5 (5)
	- incorrect comparison operator is used (-1)
	- `planets_list` data structure is not used to answer (-1)
	- plot is incorrect (-1)
	- plot is not properly labeled (-1)

- `star_classes` (3)
	- data structure is defined incorrectly (-1)
	- incorrect comparison operators are used (-1)
	- `stars_dict` data structure is not used (-1)

- q6 (3)
	- incorrect logic is used to answer (-1)
	- did not ignore the `Star` objects with missing `stellar_luminosity` data (-1)
	- `star_classes` data structure is not used to answer (-1)

- q7 (5)
	- incorrect logic is used to answer (-1)
	- `star_classes` data structure is not used to answer (-1)
	- plot is incorrect (-1)
	- plot is not properly labeled (-1)

- q8 (5)
	- incorrect comparison operator is used (-1)
	- `star_classes` data structure is not used to answer (-1)
	- plot is incorrect (-1)
	- plot is not properly labeled (-1)

- q9 (5)
	- incorrect logic is used to answer (-1)
	- `stars_dict` data structure is not used to answer (-1)
	- plot is incorrect (-1)
	- plot is not properly labeled (-1)

- `get_all_paths_in` (6)
	- hardcoding the name of directory inside the function (-1)
	- function does not remove all files and directories that start with `.` (-1)
	- function does not sort file names explicitly (-1)
	- function logic is incorrect (-2)
	- paths are hardcoded using slashes (-1)

- q10 (3)
	- `get_all_paths_in` function is not used to answer (-2)
	- paths are hardcoded using slashes (-1)

- q11 (3)
	- `get_all_paths_in` function is not used to answer (-2)
	- paths are hardcoded using slashes (-1)

- q12 (3)
	- `get_all_paths_in` function is not used to answer (-2)
	- paths are hardcoded using slashes (-1)

- q13 (3)
	- `get_all_paths_in` function is not used to answer (-2)

- `all_planets_list` (5)
	- data structure is defined incorrectly (-1)
	- `get_planets` function is not used to answer (-1)
	- `broken_data` data structure is not used to answer (-1)
	- paths are hardcoded using slashes (-1)
	- `planets_list` data structure is modified or redefined (-1)

- `get_surface_gravity` (3)
	- function did not return `None` for missing data (-1)
	- function logic is incorrect (-2)

- q14 (3)
	- `get_surface_gravity` function is not used to answer (-1)
	- `all_planets_list` data structure is not used to answer (-1)
	- did not exit loop and instead iterated further after finding the answer (-1)

- `get_distances_to_star` (3)
	- function did not return `None` for missing data (-1)
	- function logic is incorrect (-2)

- q15 (3)
	- `get_distances_to_star` function is not used to answer (-1)
	- `all_planets_list` data structure is not used to answer (-1)
	- did not exit loop and instead iterated further after finding the answer (-1)

- `get_liquid_water_distances` (3)
	- function did not return `None` for missing data (-1)
	- function logic is incorrect (-2)

- q16 (3)
	- `get_liquid_water_distances` function is not used to answer (-1)
	- `all_planets_list` data structure is not used to answer (-1)
	- did not exit loop and instead iterated further after finding the answer (-1)

- q17 (4)
	- incorrect logic is used to answer (-1)
	- `get_liquid_water_distances` function is not used to answer (-1)
	- `all_planets_list` data structure is not used to answer (-1)

- `get_surface_temperatures` (3)
	- function did not return `None` for missing data (-1)
	- function logic is incorrect (-2)

- q18 (3)
	- `get_surface_temperatures` function is not used to answer (-1)
	- `all_planets_list` data structure is not used to answer (-1)
	- did not exit loop and instead iterated further after finding the answer (-1)

- q19 (4)
	- incorrect comparison operators are used (-1)
	- `get_surface_temperatures` function is not used to answer (-1)
	- `all_planets_list` data structure is not used to answer (-1)

- q20 (5)
	- incorrect logic is used to answer (-2)
	- `get_surface_gravity`, `get_distances_to_star`, `get_liquid_water_distances`, and `get_surface_temperatures` functions are not used to answer (-1)
	- `all_planets_list` data structure is not used to answer (-1)

