paths are hardcoded using slashes

Feedback: To construct file paths in a
cross-platform manner, utilize `os.path.join()`
instead of hardcoding slashes. This approach
ensures compatibility across different operating
systems. Modify your code to employ
`os.path.join()` for assembling directory paths.