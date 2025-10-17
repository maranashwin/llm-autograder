incorrect logic is used to answer

The dataset is modified in a way that some stars
have missing `stellar_luminosity` data, some have 0 as
their `stellar_luminosity` value, and some have very high
`stellar_luminosity` values. Your code needs to correctly
skip stars with missing `stellar_luminosity` data and
calculate the average `stellar_luminosity` of the
remaining stars.