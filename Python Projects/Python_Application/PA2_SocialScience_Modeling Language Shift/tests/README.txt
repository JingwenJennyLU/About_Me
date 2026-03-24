MACS 30121: Language shifts

Format of the region files:
- the first line of each file is the grid size (N)
- subsequent N lines contain the language states of homes in the region (0, 1, or 2)
- the next line is the number of community centers in the region
- subsequent lines contain the location and service distance of the community center

Region files:

    writeup-grid.txt: The 5x5 region used in the writeup without the 
        community center. 

    writeup-grid-with-cc.txt: The 5x5 region used in the writeup,
        including the community center.

    clustered-speakers.txt: A 5x5 region where SL and DL speakers are
        in clusters, with a community center.

    mostly-DL.txt: A 5x5 region of most DL (state 0) speakers,
        with a community center.

    medium-grid.txt: A 10x10 region with two community centers.

    large-grid.txt: A 40x40 region with five community centers,
        used to test efficiency.

    The files with "-final.txt" are the final state of a test with format:
        initial-file-V-W-X-Y-Z-final.txt, where:
            V: R (neighborhood radius)
            W: A * 10 (threshold parameter)
            X: B * 10 (threshold parameter)
            Y: C * 10 (threshold parameter)
            Z: max_steps (maximum number of simulation steps)

Test files contain the parameters used by test code in ../test_run_simulation.py
    in JSON format. 

Test files:

    test_run_simulation_small.json: test parameters for the small 
        run_simulation tests.

    test_run_simulation_medium.json: test parameters for the medium 
        run_simulation tests.

    test_run_simulation_large.json: test parameters for the large 
        run_simulation tests

README.txt: This file.
