import jaro
import munkres
import json
import re

class StringMatcher:
    threshold = .8
    method = "jaro"
    references = []

    def __init__(self, ref_path='eye_reference.txt', config_path='eye_config.txt'):
        self.build_reference(ref_path)
        self.setup_config(config_path)

    def setup_config(self, config_path):
        with open(config_path) as data_file:
            data = json.load(data_file)

        self.threshold = float(data["method_type"]["parameters"]["threshold"])
        self.method = data["method_type"]["partial_method"]
        #self.threshold = 0.8

    def build_reference(self, ref_path):
        with open(ref_path) as ref_colors:
            for color in ref_colors:
                self.references.append(color)

    def levenshtein_sim(self, seq1, seq2):
        oneago = None
        thisrow = range(1, len(seq2) + 1) + [0]
        for x in xrange(len(seq1)):
            twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
            for y in xrange(len(seq2)):
                delcost = oneago[y] + 1
                addcost = thisrow[y - 1] + 1
                subcost = oneago[y - 1] + (seq1[x] != seq2[y])
                thisrow[y] = min(delcost, addcost, subcost)
        max_len = max({len(seq1),len(seq2)})
        min_len = min({len(seq1),len(seq2)})
        return float(max_len - thisrow[len(seq2) - 1])/float(min_len)

    def sim_metric(self, word1, word2):
        if self.method == "jaro":
            return jaro.metric_jaro_winkler(word1,word2)
        else:
            return self.levenshtein_sim(word1,word2)

    def sim_measure(self, str1, str2):
        str1_words = str1.split()
        str2_words = str2.split()

        outer_arr = []
        for in_word in str1_words:
            inner_arr = []
            for ref_word in str2_words:
                sim = self.sim_metric(in_word, ref_word)
                if sim < self.threshold:
                    sim = 0.0
                inner_arr.append(1.0 - sim)
            outer_arr.append(inner_arr)
        if len(outer_arr) == 0:
            return 0.0
        m = munkres.Munkres()
        indexes = m.compute(outer_arr)
        values = []
        for row, column in indexes:
            values.append(1.0 - outer_arr[row][column]) #go back to similarity
        return sum(values)/(len(str1_words)+len(str2_words)-len(values)+values.count(0.0))

    def findBestMatch(self, input):
        similarities = []
        for r in self.references:
            sim_index = self.sim_measure(input,r)
            similarities.append(sim_index)
            #print(r+" "+str(sim_index))
        max_sim = max(similarities)
        if max_sim < 1e-20:
            return 'NONE'
        return self.references[similarities.index(max_sim)]

colors = []
sm = StringMatcher('reference-colors2.txt', 'config_eye.json')
with open("sentences.txt") as input:
    for line in input:
        line = line.lower()
        #args = re.search('([0-9]+) <(.*)> (.*)', line)
        #match = sm.findBestMatch(args.group(3))
        match = sm.findBestMatch(line)
        print(line + " => " + match)
