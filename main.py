import argparse
from energybot.bot import main
from energybot.tasks.worker import run_worker
from energybot.tasks.sync import run_sync

parser = argparse.ArgumentParser()
parser.add_argument('--run', help='Enter usage command')
args = parser.parse_args()

if __name__ == "__main__":
    if args.run == 'sync':
        run_sync()
    elif args.run == 'worker':
        run_worker()
    else:
        main()