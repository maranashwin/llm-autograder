hardcoding the name of directory inside the function

The function failed a test where directories with
names other than "sample_data" were used. Verify
that your function does not include hardcoded
directory names, and ensure it's written to accept
any given directory as an argument. Use the
provided `directory` parameter to build your file
paths.