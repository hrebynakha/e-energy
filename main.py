import argparse
from energybot.bot import main
parser = argparse.ArgumentParser()
parser.add_argument('--run', help='Enter usage command')
args = parser.parse_args()

if __name__ == "__main__":
    main(args)