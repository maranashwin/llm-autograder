paths are hardcoded using slashes

Check that you're using `os.path.join` for
platform-independent path construction. Avoid
hardcoding slashes, and ensure the
`get_all_paths_in` function is called correctly.
Consider different operating systems when
constructing file paths.