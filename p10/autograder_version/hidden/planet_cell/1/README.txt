function does not typecast values based on columns

This test checks whether your function correctly
preprocesses and typecasts values according to
their corresponding column types. For example,
numeric columns should return float values, and
textual columns should return string values. This
is checked by running your function on various
columns and analyzing the data types of the
returned values. The intention is to ensure your
function effectively automates this process, thus
reducing the need for additional manual
typecasting.