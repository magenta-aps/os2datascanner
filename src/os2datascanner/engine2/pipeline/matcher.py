from os import getpid

from ...utils.prometheus import prometheus_session
from ..rules.rule import Rule
from ..conversions.types import decode_dict
from .utilities import (notify_ready, PikaPipelineRunner, notify_stopping,
        prometheus_summary, make_common_argument_parser)


def message_received_raw(body, channel, matches_q, handles_q, conversions_q):
    progress = body["progress"]
    representations = decode_dict(body["representations"])
    rule = Rule.from_json_object(progress["rule"])

    new_matches = []

    # Keep executing rules for as long as we can with the representations we
    # have
    while not isinstance(rule, bool):
        head, pve, nve = rule.split()

        target_type = head.operates_on
        type_value = target_type.value
        if type_value not in representations:
            # We don't have this representation -- bail out
            break
        representation = representations[type_value]

        matches = list(head.match(representation))
        new_matches.append({
            "rule": head.to_json_object(),
            "matches": matches if matches else None
        })
        if matches:
            rule = pve
        else:
            rule = nve

    if isinstance(rule, bool):
        # We've come to a conclusion!
        yield (matches_q, {
            "scan_spec": body["scan_spec"],
            "handle": body["handle"],
            "matched": rule,
            "matches": progress["matches"] + new_matches
        })
        # Only trigger metadata scanning if the match succeeded
        if rule:
            yield (handles_q, {
                "scan_tag": body["scan_spec"]["scan_tag"],
                "handle": body["handle"]
            })
    else:
        # We need a new representation to continue
        yield (conversions_q, {
            "scan_spec": body["scan_spec"],
            "handle": body["handle"],
            "progress": {
                "rule": rule.to_json_object(),
                "matches": progress["matches"] + new_matches
            }
        })


def main():
    parser = make_common_argument_parser()
    parser.description = ("Consume representations and generate matches"
            + " and fresh conversions.")

    inputs = parser.add_argument_group("inputs")
    inputs.add_argument(
            "--representations",
            metavar="NAME",
            help="the name of the AMQP queue from which representations"
                    + " should be read",
            default="os2ds_representations")

    outputs = parser.add_argument_group("outputs")
    outputs.add_argument(
            "--matches",
            metavar="NAME",
            help="the name of the AMQP queue to which matches should be"
                    + " written",
            default="os2ds_matches")
    outputs.add_argument(
            "--conversions",
            metavar="NAME",
            help="the name of the AMQP queue to which conversions should be"
                    + " written",
            default="os2ds_conversions")
    outputs.add_argument(
            "--handles",
            metavar="NAME",
            help="the name of the AMQP queue to which handles (for metadata"
                    + " extraction) should be written",
            default="os2ds_handles")

    args = parser.parse_args()

    class MatcherRunner(PikaPipelineRunner):
        @prometheus_summary(
                "os2datascanner_pipeline_matcher", "Representations examined")
        def handle_message(self, body, *, channel=None):
            if args.debug:
                print(channel, body)
            return message_received_raw(body, channel,
                    args.matches, args.handles, args.conversions)

    with prometheus_session(
            str(getpid()),
            args.prometheus_dir,
            stage_type="matcher"):
        with ExporterRunner(
                read=[args.representations],
                write=[args.handles, args.matches, args.conversions],
                heartbeat=6000) as runner:
            try:
                print("Start")
                notify_ready()
                runner.run_consumer()
            finally:
                print("Stop")
                notify_stopping()


if __name__ == "__main__":
    main()
