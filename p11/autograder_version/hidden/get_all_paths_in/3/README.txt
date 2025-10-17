function does not sort file names explicitly

Ensure your function explicitly sorts files after
listing them with `os.listdir`, as the order
returned is not guaranteed across different
environments. Check your recursive implementation
for sorting consistency.