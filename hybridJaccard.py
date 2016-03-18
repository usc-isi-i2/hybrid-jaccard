import jaro
import munkres
import json
import re

class HybridJaccard(object):
    def __init__(self, ref_path='eye_reference.txt', config_path='eye_config.txt',
                 threshold = 0.8,
                 method = "jaro"):
        self.threshold = threshold
        self.method = method
        self.setup_sim_metric()
        self.reference_words = []
        self.labels = []
        self.cache = {}
        self.m = munkres.Munkres() # Create a Munkres object, which can be used multiple times.
        self.build_reference(ref_path)
        self.setup_config(config_path)

    def setup_config(self, config_path):
        """Read the configuration file, extracting the method name and threshold."""
        with open(config_path, 'r') as data_file:
            self.data = json.load(data_file)

        self.threshold = float(self.data["method_type"]["parameters"]["threshold"])
        self.method = self.data["method_type"]["partial_method"]
        self.setup_sim_metric()

    def build_reference(self, ref_path):
        """Read the reference file, building the lists of reference words and the resulting labels."""
        with open(ref_path, 'r') as ref_colors:
            for line in ref_colors:
                main, _, synonyms = line.partition(":")
                synonyms = [s.strip() for s in synonyms.split(',')]
                main = main.strip()
                self.reference_words.append(main.split())
                self.labels.append(main)
                for synonym in synonyms:
                    if synonym:
                        self.reference_words.append(synonym.split())
                        self.labels.append(main)

    def jaro_winkler_sim(self, seq1, seq2):
        return jaro.metric_jaro_winkler(seq1, seq2)

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

    def setup_sim_metric(self):
        """Save the current metric function in sim_metric."""
        if self.method == "jaro":
            self.sim_metric = self.jaro_winkler_sim
        else:
            self.sim_metric = self.levenshtein_sim
        
    def sim_measure(self, str1_words, str2_words):
        """Measure the similarity between two strings of words, using the word-comparison similarity metric function pointed to by sim_metric."""
        if len(str1_words) == 0 or len(str2_words) == 0:
            return 0.0 # defensive check.  Might want to complain here.
        outer_arr = []
        for in_word in str1_words:
            inner_arr = []
            for ref_word in str2_words:
                sim = self.sim_metric(in_word, ref_word)
                if sim < self.threshold:
                    sim = 0.0
                inner_arr.append(1.0 - sim)
            outer_arr.append(inner_arr)
        values = []
        indexes = self.m.compute(outer_arr)
        for row, column in indexes:
            values.append(1.0 - outer_arr[row][column]) #go back to similarity
        return sum(values)/(len(str1_words)+len(str2_words)-len(values)+values.count(0.0))

    def findBestMatch(self, input_str):
        """Find the best match, without caching the result. Use if input strings do not repeat often."""
        input_words = input_str.split()
        max_sim = 0 # chosen to return NONE if reference_words is empty.
        max_sim_index = 0 # initial value does not matter
        for idx, ref_words in enumerate(self.reference_words):
            similarity = self.sim_measure(input_words, ref_words)
            if similarity > max_sim:
                max_sim = similarity
                max_sim_index = idx
        if max_sim < 1e-20: # Shouldn't this threshold be parameterized?
            return 'NONE'
        return self.labels[max_sim_index]

    def findBestMatchCached(self, input_str):
        """Find the best match, caching the result.  Use if input strings will repeat often."""
        result = self.cache.get(input_str)
        if result is None:
            result = self.findBestMatch(input_str)
            self.cache[input_str] = result
        return result

# call main() if this is run as standalone
if __name__ == "__main__":
    colors = []
    sm = HybridJaccard()
    with open("input.txt") as input:
        for line in input:
            line = line.strip()
            #line = line.lower()
            args = re.search('([0-9]+) <(.*)> (.*)', line)
            #print(args.group(3))
            match = sm.findBestMatchCached(args.group(3))
            #match = sm.findBestMatch(line)
            print(line+" => "+match)
            
    # test for non-default reference sets
    print "hair-reference:"
    h = HybridJaccard(ref_path='hair_reference.txt', config_path='hair_config.txt')
    print "long blond hair => " + h.findBestMatch(u'long blond hair')
    print "platinum hair => " + h.findBestMatch(u'platinum hair')

    print "eye-reference:"
    e = HybridJaccard(ref_path='eye_reference.txt', config_path='eye_config.txt')
    print "beautiful blue eyes => " + e.findBestMatch(u'beautiful blue eyes')
    print "eyes of green => " + e.findBestMatch(u'eyes of green')

