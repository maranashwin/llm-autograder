did not ignore the `Star` objects with missing `stellar_luminosity` data

Check for `None` values when computing average
luminosity. Modify the code to skip stars with
missing `stellar_luminosity` data. Consider using
an `if` condition to filter out such cases.