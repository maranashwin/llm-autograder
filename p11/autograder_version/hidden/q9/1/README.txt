incorrect logic is used to answer

Check that you properly handled cases with missing
data. Verify the filtering logic to make sure that
only stars with all attributes
(`stellar_effective_temperature`,
`stellar_luminosity`, `stellar_age`,
`stellar_mass`) present are included in the lists.
Consider edge cases such as zero values which may
not be intended as missing data.