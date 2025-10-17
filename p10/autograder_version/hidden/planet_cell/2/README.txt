column indices are hardcoded instead of using column names

This test checks if your function correctly uses
column names to find the index, instead of relying
on hardcoded indices. To do this, the columns in
the datasets are shuffled around in various ways.
If your function relies on hardcoded indices, this
test can highlight that issue since the correct
data will not be extracted due to the permutation
of columns.