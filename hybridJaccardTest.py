import argparse
import sys
import hybridJaccard as hj

def main():
    "Command line testinterface."

    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--configFile', help="Configuration file (JSON).", required=False)
    parser.add_argument('-i','--input', help="Input file of phrases to test.", required=True)
    parser.add_argument('-r','--referenceFile', help="Reference file.", required=False)
    args = parser.parse_args()

    sm = hj.HybridJaccard(ref_path=args.referenceFile, config_path=args.configFile)
    with open("input.txt") as input:
        for line in input:
            line = line.strip()
            match = sm.findBestMatchStringCached(line)
            if match is None:
                match = "(NONE)"
            print(line+" => "+match)

# call main() if this is run as standalone
if __name__ == "__main__":
    sys.exit(main())
