answer unnecessarily iterates over the entire dataset

The test is checking whether you are unnecessarily
iterating over the entire dataset in order to
extract the data for the third Star. Make sure you
are only using the row index of the third star to
extract its data, without iterating over all the
rows. There is code injected that tracks how
many times the `star_cell` function is called, so
be careful to use the correct method for
extracting the data.