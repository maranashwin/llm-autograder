# Project 7 (P7) Grading Rubric


## Code reviews

- The Gradescope autograder will make deductions based on the rubric provided below.
- To ensure that you don't lose any points, you must **review** the rubric and make sure that you have followed the instructions provided in the project correctly.
- If you **fail** the **public tests** for a function or **hardcode** the answers to that question, you will automatically lose **all** points for that question.

## Rubric

### General guidelines:

- Did not save the notebook file prior to running the cell containing "export". We cannot see your output if you do not save before generating the zip file. This deduction will become stricter for future projects. (-3)
- Used concepts/modules such as pandas not covered in class yet - built-in functions that you have been introduced to can be used. (-3)
- Import statements are not all placed at the top of the notebook. (-1)

### Question specific guidelines:

- `format_euros` (3)
	- function logic is incorrect when the input ends with `"K"` (-1)
	- function logic is incorrect when the input ends with `"M"` (-1)
	- function logic is incorrect when the input does not end with `"K"` or `"M"` (-1)

- `cell` (5)
	- variables `csv_data`, `csv_header`, and `csv_rows` are not defined as expected (-1)
	- function does not typecast the correct columns to `int` or `float` as expected (-1)
	- function does not format the `Height` column correctly (-1)
	- function does not use `format_euros` to format the relevant columns (-1)
	- function typecasts based on the column index and not the `col_name` (-1)

- `players` (5)
	- data structure is not defined correctly (-2)
	- logic used to define data structure is incorrect (-2)
	- `cell` function is not used to read data (-1)

- q1 (2)
	- `players` data structure is not used to read data (-2)

- q2 (4)
	- incorrect logic is used to find the player with the highest `Value` (-1)
	- incorrect logic is used to find the statistics of the player with the highest `Value` (-1)
	- `players` data structure is not used to read data (-1)

- q3 (4)
	- incorrect logic is used to find the player with the highest `Wage` (-1)
	- incorrect logic is used to find the `Nationality` of the player with the highest `Wage` (-1)
	- `players` data structure is not used to read data (-1)

- q4 (3)
	- the player with the highest `Wage` is recomputed (-1)
	- incorrect logic is used to find the `Position` of the player with the highest `Wage` (-1)
	- `players` data structure is not used to read data (-1)

- q5 (3)
	- incorrect logic is used to answer (-1)
	- teams whose `League` is not exactly as required are added to the list (-1)
	- `players` data structure is not used to read data (-1)

- q6 (4)
	- incorrect logic is used to answer (-1)
	- the keys of `preferred_foot_count` are hardcoded (-1)
	- `players` data structure is not used to read data (-1)

- q7 (5)
	- incorrect logic is used to answer (-2)
	- the keys of `preferred_foot_avg_overall` are hardcoded (-1)
	- `players` data structure is not used to read data (-1)

- q8 (4)
	- incorrect logic is used to answer (-1)
	- the keys of `positions_count` are hardcoded (-1)
	- `players` data structure is not used to read data (-1)

- q9 (5)
	- incorrect logic is used to answer (-2)
	- the keys of `positions_avg_age` are hardcoded (-1)
	- `players` data structure is not used to read data (-1)

- q10 (5)
	- incorrect logic is used to answer (-2)
	- the keys of `positions_avg_height` are hardcoded (-1)
	- `players` data structure is not used to read data (-1)

- `average_stat_by_position` (4)
	- function logic is incorrect (-2)
	- function only works for certain numerical columns (-1)
	- `players` data structure is not used to read data (-1)

- q11 (2)
	- `average_stat_by_position` function is not used to answer (-2)

- q12 (2)
	- `average_stat_by_position` function is not used to answer (-2)

- q13 (4)
	- incorrect logic is used to answer (-2)
	- `average_stat_by_position` function is not used to answer (-1)

- `best_player_of_team_at_position` (5)
	- function logic is incorrect when there is a unique best player of the `team` at `position` (-2)
	- function logic is incorrect when there are multiple players tied for best player of the `team` at `position` (-1)
	- function logic is incorrect when there are no players of the `team` at `position` (-1)
	- `players` data structure is not used to read data (-1)

- q14 (2)
	- `best_player_of_team_at_position` function is not used to answer (-2)

- q15 (3)
	- `best_player_of_team_at_position` function is not used to answer (-2)
	- `players` data structure is not used to read data (-1)

- `best_starting_players_of` (5)
	- function logic is incorrect (-2)
	- all positions are looped through instead of just the unique positions (-1)
	- `best_player_of_team_at_position` function is not used to answer (-1)
	- `players` data structure is not used to read data (-1)

- q16 (2)
	- `best_starting_players_of` function is not used to answer (-2)

- q17 (4)
	- incorrect logic is used to answer (-1)
	- `best_starting_players_of` function is not used to answer (-1)
	- `players` data structure is not used to read data (-1)

- q18 (5)
	- incorrect logic is used to answer (-2)
	- `best_starting_players_of` function is not used to find the best starting players (-1)
	- `players` data structure is not used to read data (-1)

- q19 (6)
	- incorrect logic is used to answer (-2)
	- best starting players of a single team is computed more than once (-1)
	- the list of unique teams in the league is recomputed (-1)
	- `best_starting_players_of` function is not used to answer (-1)
	- `players` data structure is not used to read data (-1)

- q20 (4)
	- incorrect logic is used to answer (-2)
	- `avg_attacking_prem_league` is not used to answer (-1)

