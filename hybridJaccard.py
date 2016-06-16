import jaro
import munkres
import json

class HybridJaccard(object):
    def __init__(self, ref_path=None, config_path=None,
                 threshold = 0.8,
                 method_type="method_type",
                 method = "jaro"):
        self.threshold = threshold
        self.method_type = method_type
        self.set_sim_metric(method)
        self.reference_phrases = []
        self.labels = []
        self.cache = {}
        self.m = munkres.Munkres() # Create a Munkres object, which can be used multiple times.
        if ref_path is not None:
            self.read_reference_file(ref_path)
        if config_path is not None:
            self.read_config_file(config_path)

    def read_reference_file(self, ref_path):
        """Read the reference file, building the lists of reference words and the resulting labels."""
        with open(ref_path, 'r') as ref_lines:
            for ref_line in ref_lines:
                self.build_references(ref_line)

    def build_references(self, ref_line):
        main_phrase, _, equivalents = ref_line.partition(":")
        equivalent_phrases = [s.strip() for s in equivalents.split(',')]
        main_phrase = main_phrase.strip()
        if not main_phrase in self.labels:
            # Record only unique instances.
            #
            # TODO: It should be an error for a main phrase to match a
            # previously declared equivalent phrase.
            main_phrase_words = main_phrase.split()
            self.reference_phrases.append(main_phrase_words)
            self.labels.append(main_phrase_words)
        for equivalent_phrase in equivalent_phrases:
            if equivalent_phrase and not equivalent_phrase in self.labels:
                # Skip empty phrases. If an equivalent phrase occurs multiple times,
                # keep the first mapping and ignore the rest.
                #
                # TODO: It should be an error for an equivalent phrase to occur
                # multiple times or to match a main phrase.
                self.reference_phrases.append(equivalent_phrase.split())
                self.labels.append(main_phrase.split())

    def read_config_file(self, config_path):
        """Read the configuration file, extracting the method name and threshold."""
        with open(config_path, 'r') as data_file:
            self.build_configuration(json.load(data_file))

    def build_configuration(self, data):
        method_data = data.get(self.method_type)
        if method_data:
            parameters = method_data.get("parameters")
            if parameters:
                threshold_string = parameters.get("threshold")
                if threshold_string:
                    self.threshold = float(threshold_string)
            method = method_data.get("partial_method")
            if method:
                self.set_sim_metric(method)
        references = method_data.get("references")
        if references:
            for ref_line in references:
                self.build_references(ref_line)
        referencesFiles = method_data.get("references_files")
        if referencesFiles:
            for ref_file in referencesFiles:
                self.read_reference_file(ref_file)

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

    def set_sim_metric(self, method):
        """Save the current metric function in sim_metric."""
        self.method = method
        if method == "jaro":
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

    def findBestMatchWords(self, input_words):
        """Find the best match, without caching the result. Call directly if input
        word sequences do not repeat often, otherwise use of the cache is
        recommended. Returns the singleton value None (not the string "NONE")
        if no match is found.

        """
        max_sim = 0 # chosen to return None if reference_phrases is empty.
        max_sim_index = 0 # initial value does not matter
        for idx, ref_words in enumerate(self.reference_phrases):
            similarity = self.sim_measure(input_words, ref_words)
            if similarity > max_sim:
                max_sim = similarity
                max_sim_index = idx
        if max_sim < 1e-20: # Shouldn't this threshold be parameterized?
            return None
        return self.labels[max_sim_index]

    def findBestMatchWordsCached(self, input_words):
        """Find the best match, caching the result.  Use if input word sequences will
        repeat often. Returns the singleton value None (not the string "NONE")
        if no match is found.

        """
        # Build a single string for cache lookup:
        #
        # TODO: The join character should be parameterized for special occasions.
        input_str = " ".join(input_words)
        # Look for the string in the cache.  None is an allowable result, so
        # use False to indicate that an entry was not found.
        result = self.cache.get(input_str, False)
        if result is False:
            result = self.findBestMatchWords(input_words)
            self.cache[input_str] = result
        return result

    def findBestMatchString(self, input_str):
        """Find the best match, without caching the result. The input is a string,
        which will be split on white space into words. Use if input strings do
        not repeat often. Returns the singleton value None (not the string
        "NONE") if no match is found, otherwise returns a string result.

        """
        result = self.findBestMatchWords(input_str.split())
        if result:
            result = " ".join(result)
        return result
        

    def findBestMatchStringCached(self, input_str):
        """Find the best match, caching the result.  The input is a string, which will
        be split on white space into words. Use if input strings will repeat
        often. Returns the singleton value None (not the string "NONE") if no
        match is found, otherwise returns a string result.

        """
        # Look for the string in the cache.  None is an allowable result, so
        # use False to indicate that an entry was not found.
        result = self.cache.get(input_str, False)
        if result is False:
            result = self.findBestMatchString(input_str)
            self.cache[input_str] = result
        return result
