all positions are looped through instead of just the unique positions

Check for duplicate positions before looping and
eliminate them to improve function efficiency.
Ensure your code does not handle the same position
multiple times, which would cause unnecessary
repeated calls to
`best_player_of_team_at_position`. Also ensure
that inside the loop, you create a variable to
store the output of `best_player_of_team_at_position`
instead of calling it multiple times.