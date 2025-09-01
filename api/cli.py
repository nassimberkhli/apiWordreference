import argparse
from presentation import print_available_dictionaries

class ListDictCodes(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, nargs=0, default=argparse.SUPPRESS, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        print_available_dictionaries()
        parser.exit()

def parse_arguments() :
    parser = argparse.ArgumentParser(description="Get translation from wordreference.com")
    parser.add_argument("dictionary_code", help="Dictionary code, use -l to list available dictionaries", metavar="DICTIONARY_CODE")
    parser.add_argument("-l", "--list-available-dictionaries", help="List available dictionaries and their codes", action=ListDictCodes)
    parser.add_argument("-a", "--audio", help="Download audio files to current directory (when available)", action='store_true')
    parser.add_argument("-s", "--sentences", help="Get only example sentences and their meaning (when available)", action='store_true')
    parser.add_argument("word", help="Word to translate")
    return parser.parse_args()
