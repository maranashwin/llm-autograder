function did not return `None` for missing data

Ensure your function checks for `None` in both
`eccentricity` and `semi_major_radius` fields of
the `Planet` object. If either is `None`, the
function should return `None`. Check your
conditionals to correctly handle missing data.