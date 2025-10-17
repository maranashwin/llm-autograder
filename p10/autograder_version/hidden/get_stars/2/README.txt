hardcoded the name of directory inside the function instead of passing it as a part of the input argument

The test is checking if you have hardcoded the
name of the directory in the `get_stars` function
instead of passing it as a part of the input
argument. The test injects code that calls the
function on files that are not inside the `data`
directory. If your function is not able to read
these files correctly, it suggests that the
directories may be hardcoded in your function.
Make sure to pass the directory as a part of the
input argument to make your function more
flexible.