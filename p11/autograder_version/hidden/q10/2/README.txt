paths are hardcoded using slashes

Ensure you are using `os.path.join` when
constructing file paths to maintain cross-platform
compatibility. Avoid hardcoding path separators.
Use the provided `get_paths_in` function to list
directory contents. Check the use of
`os.path.join` in your code.