MACS 30121 Programming Assignment #6: Avian Biodiversity Treemaps
This is a programming project from The University of Chicago MACS 30121 (Designed by Dr. Zhao Wang)
-------------------------------------------------------------

These are the files for Programming Assignment #6.

- treemap.py: Skeleton Code

- tree.py: Python file that provides a Tree class.

- drawing.py: Python file that provides a function for visualizing a list
  of rectangles.

- test_treemap.py: Python file with the automated tests for this assignment.

- get_files.sh: A script for downloading the data. See the programming 
  assignment writeup for instructions on how to run it. Running it will add two
  new directories: data/ and test_data/
  - data:
    - birds.json: JSON file containing trees of bird sighting data.
    - sparrows.json: JSON file containing trees in which all of the root's 
      children are leaves.
  - test_data: directory containing files for running the automated tests
    - expected_birds_rectangles.json
    - expected_birds_values_paths.json
    - expected_sparrows_rectangles.json

- pytest.ini: A configuration file that you can safely ignore.

- README.txt: this file.
