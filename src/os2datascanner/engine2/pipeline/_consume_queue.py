from sys import argv
import traceback

from .utilities import make_common_argument_parser, PikaConnectionHolder


def main(*arguments):
    parser = make_common_argument_parser()
    parser.description = "Consume all of the objeccs in a queue."

    parser.add_argument(
            "queue",
            nargs="+",
            choices=("os2ds_scan_specs", "os2ds_conversions",
                    "os2ds_representations", "os2ds_matches",
                    "os2ds_handles", "os2ds_metadata", "os2ds_problems",
                    "os2ds_results",),
            metavar="NAME",
            help="the AMQP queues from which objects should be read and"
                    " discarded",
            default=["os2ds_scan_specs"])

    args = parser.parse_args(arguments)

    with PikaConnectionHolder(host=args.host, heartbeat=6000) as ch:
        for q in args.queue:
            try:
                print("Purging queue {0}".format(q))
                ch.channel.queue_declare(q, passive=True)
                ch.channel.queue_purge(q)
            except Exception:
                traceback.print_exc()
                ch.clear()
                print("continuing anyway!")


if __name__ == "__main__":
    main(*argv)
