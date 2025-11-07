import os
import sys
import argparse
import django
from energybot.helpers.logger import logger
from energybot.tasks.sync import run_sync
from energybot.bot import bot
from energybot.tasks.worker import run_worker

parser = argparse.ArgumentParser()
parser.add_argument("--run", help="Enter usage command")
parsed_args = parser.parse_args()


def main(args):
    """Main function for running bot"""
    if args.run == "sync":
        logger.info("Sync started")
        run_sync()
    elif args.run == "worker":
        logger.info("Worker started")
        run_worker()
    elif args.run == "bot":
        logger.info("Bot started")
        bot.infinity_polling()
    else:
        logger.info("Executing django server command...")
        os.environ.setdefault(
            "DJANGO_SETTINGS_MODULE", "energybot.web.energyweb.settings"
        )
        django.setup()
        from django.core.management import (
            execute_from_command_line,
        )

        execute_from_command_line(["manage", args.run])
        sys.exit(0)


if __name__ == "__main__":
    main(parsed_args)
