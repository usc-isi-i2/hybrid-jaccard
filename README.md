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
match = sm.findBestMatchString("beautiful light bluish eyes")

If the match fails, it will return the singleton value None.

Other matching calls are:

match = sm.findBestMatchStringCached("beautiful light bluish eyes")

match = sm.findBestMatchWords(["beautiful", "light", "bluish", "eyes"])

match = sm.findBestMatchWordsCached(["beautiful", "light", "bluish", "eyes"])

The "Cached" variants maintain a local cache of previously tested phrases.

Here is a sample configuration file ("hybrid_jaccard_config.json"):

{
  "eyeColor": {
    "type": "hybrid_jaccard",
    "partial_method": "jaro",
    "parameters": {
      "threshold": "0.90"
    },
    "references": [
        "blue",
        "green",
        "brown",
        "hazel",
        "gray:grey"
    ]
  },
  "hairType": {
    "type": "hybrid_jaccard",
    "partial_method": "jaro",
    "parameters": {
      "threshold": "0.90"
    },
    "references": [
        "long",
        "curly",
        "blonde: blond",
        "brunette",
        "brown: chestnut",
        "black",
        "red: redhead",
        "auburn: reddish brown",
        "pink"
    ]
  }
}

The outer dictionary can be used to select the rules used by a specific
HybridJaccard instance, controlled by the "method_type" parameter in
in object creation.  For example:

sm = HybridJaccard(method_type="eyeColor")

The inner dictionary:

-- has a field "type" which is for now always "hybrid_jaccard",
-- has a field "partial_method" which can be "jaro" or "levenshtein",
-- has a field "threshold" which determines how picky we want to be in hybrid
   jaccard algorithm before doing the matching,
-- can included reference data as strings, or
-- can include the names of reference data files:

   "reference_files": [ "eye_color.txt" ]

	Reference data may be supplied inside the selected part of the
configuration file, from files referenced in the configuration file (the
reference_files list is not restricted to a single file), and in a file whose
name is passed to HybridJaccard object initialization.  When multiple sources
are supplied, they aee merged.  Sample eye color references are:

amber
blue: azure, sapphire
brown
gray
green
hazel
red
violet

	The first set of whitespace-separated words on a line is a reference
phrase.  if there is a colon, it may be followed by a comma-separated list of
phrases (aliases).  The aliases will be mapped to the main (left-side) phrase.

Samples:

The "samples" folder is intended to hold sample files for testing
HybridJaccard.  There is one sample folder at present:

hbase-dump-2015-10-01-2015-12-01-aman-hbase/

This folder contains:

2 original sample files:

hbase-dump-2015-10-01-2015-12-01-aman-hbase-crf-hair-eyes-sample.txt
hbase-dump-2015-10-01-2015-12-01-aman-hbase-crf-name-ethnic-sample.txt

2 intermediary files:

hbase-dump-2015-10-01-2015-12-01-aman-hbase-crf-hair-eyes-sample.jsonl
hbase-dump-2015-10-01-2015-12-01-aman-hbase-crf-name-ethnic-sample.jsonl

6 final sample files:

hbase-dump-2015-10-01-2015-12-01-aman-hbase-crf-eyes-sample.jsonl
hbase-dump-2015-10-01-2015-12-01-aman-hbase-crf-hair-sample.jsonl

hbase-dump-2015-10-01-2015-12-01-aman-hbase-crf-B_ethnic-sample.jsonl
hbase-dump-2015-10-01-2015-12-01-aman-hbase-crf-B_workingname-sample.jsonl
hbase-dump-2015-10-01-2015-12-01-aman-hbase-crf-I_ethnic-sample.jsonl
hbase-dump-2015-10-01-2015-12-01-aman-hbase-crf-I_workingname-sample.jsonl

