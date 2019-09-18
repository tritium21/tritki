import argparse
import sys

import tritki.app

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--data-path', help="Path to wiki directory")
    parser.add_argument('--create', action='store_true')
    parsed, unparsed = parser.parse_known_args(argv)
    args = vars(parsed)
    args['qt_args'] = unparsed
    app = tritki.app.App(**args)
    return