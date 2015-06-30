# hybrid-jaccard
Implementation of hybrid jaccard similarity

Package files:
|
|-> __init__.py
|
|-> hybrid_jaccard.py: contains the base class for hybrid jaccard string matching
|
|-> jaro.py & typo_tables.py: contain the methods for jaro distance calculation
|
|-> munkres.py: contains the hungarian matching algorithm
|
|-> eye_config.txt: contains the configuration info for the hybrid-jaccard class
|
|-> eye_reference.txt: contains the reference eye colors
|
|-> input.txt: a sample input file for testing the program
|
|-> README.md
|
|-> LICENSE

Usage:

You should import "HybridJaccard" in your code. The main class is HybridJaccard.
The class constructor gets two arguments, path to reference and config files respectively.
The "findBestMatch" method returns the best match for the input string among those in the 
reference file if one exists, and returns "NONE" otherwise. A sample usage might be like:

sm = HybridJaccard()
match = sm.findBestMatch("beautiful light bluish eyes")

about eye_config.txt:
-- it has a field "type" which is for now always "hybrid_jaccard"
-- it has a field "partial_method" which can be "jaro" or "levenshtein"
-- it has a field "threshold" which determines how picky we want to be in hybrid jaccard algorithm before doing the matching


