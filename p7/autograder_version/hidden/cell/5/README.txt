function typecasts based on the column index and not the `col_name`

Check that your `cell` function dynamically
locates the column index using the `col_name` and
does not rely on hardcoded indices, as column
order may change. Ensure typecasting is done
correctly based on column name, not index.