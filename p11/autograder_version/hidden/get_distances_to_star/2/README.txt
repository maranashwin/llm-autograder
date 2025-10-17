function logic is incorrect

Check that your function correctly accounts for
the absence of `eccentricity` or
`semi_major_radius` attributes in a `Planet`
object. If either is missing or `None`, the
function should return `None`. Ensure you are
calculating the shortest and longest distances
with the correct formula: `semi_major * (1 -
absolute_value_of_eccentricity)` and `semi_major *
(1 + absolute_value_of_eccentricity)`,
respectively.