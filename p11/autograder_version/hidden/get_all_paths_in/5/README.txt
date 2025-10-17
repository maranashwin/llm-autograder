paths are hardcoded using slashes

Ensure you use `os.path.join` for cross-platform
compatibility instead of hardcoded paths. The test
modifies your code to use a `new_join` function
that concatenates with `&`. Check for proper use
of `os.path.join` in your function.