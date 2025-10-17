function is called more than twice with the same dataset

You are tasked with writing a function that reads
data from a CSV file and a JSON file and returns a list
containing detailsstar of planets. However, you
need to make sure that you do not read the same
file multiple times, as it is time-consuming.
Instead, you should store the data in a variable
after reading it once, and access the variable in
future calls. Be aware that there may be injected
code that tracks how many times each file is
provided as input. Make sure your function is not
called on any file more than twice.