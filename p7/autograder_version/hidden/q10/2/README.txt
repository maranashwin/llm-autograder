the keys of `positions_avg_height` are hardcoded

Ensure positions are dynamically determined from
the dataset and not hardcoded. Check how you
retrieve and aggregate `Position` data, and use
looping constructs to handle different `Position`
values present in the `players` dictionary.