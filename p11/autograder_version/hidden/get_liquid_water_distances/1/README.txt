function did not return `None` for missing data

Ensure `get_liquid_water_distances` function
checks for `None` before computing distances.
Review how missing `stellar_luminosity` data is
handled in your function. Revisit the logic for
returning `None` if the data is missing or
incomplete.