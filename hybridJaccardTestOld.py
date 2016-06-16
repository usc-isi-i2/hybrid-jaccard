import re
import sys
import hybridJaccard as hj

def main():
    colors = []
    sm = hj.HybridJaccard(ref_path='eye_reference.txt', config_path='eye_config.txt')
    with open("input.txt") as input:
        for line in input:
            line = line.strip()
            #line = line.lower()
            args = re.search('([0-9]+) <(.*)> (.*)', line)
            #print(args.group(3))
            match = sm.findBestMatchStringCached(args.group(3))
            if match is None:
                match = "NONE"
            #match = sm.findBestMatch(line)
            print(line+" => "+match)
            
    # test for non-default reference sets
    print "hair-reference:"
    h = hj.HybridJaccard(ref_path='hair_reference.txt', config_path='hair_config.txt')
    print "long blond hair => " + h.findBestMatchString(u'long blond hair')
    print "platinum hair => " + h.findBestMatchString(u'platinum hair')

    print "eye-reference:"
    e = hj.HybridJaccard(ref_path='eye_reference.txt', config_path='eye_config.txt')
    print "beautiful blue eyes => " + e.findBestMatchString(u'beautiful blue eyes')
    print "eyes of green => " + e.findBestMatchString(u'eyes of green')


# call main() if this is run as standalone
if __name__ == "__main__":
    sys.exit(main())
