"""
Auditable Server Sessions - Example Outputs
Example methods demonstrating output destinations for logs generated by
audited server sessions.

This is designed to be a single source of events for developers to customize
and add any additional enhancements before events are written out-- i.e. if you
want to keep a running list of what IPs a user logs in from on account/character
objects, or if you want to perform geoip or ASN lookups on IPs before committing,
or tag certain events with the results of a reputational lookup, this should be
the easiest place to do it. Write a method and invoke it via
`settings.AUDIT_CALLBACK` to have log data objects passed to it.

Evennia contribution - Johnny 2017
"""

import json
import syslog

from evennia.utils.logger import log_file


def to_file(data):
    """
    Writes dictionaries of data generated by an AuditedServerSession to files
    in JSON format, bucketed by date.

    Uses Evennia's native logger and writes to the default
    log directory (~/yourgame/server/logs/ or settings.LOG_DIR)

    Args:
        data (dict): Parsed session transmission data.

    """
    # Bucket logs by day and remove objects before serialization
    bucket = data.pop("objects")["time"].strftime("%Y-%m-%d")

    # Write it
    log_file(json.dumps(data), filename="audit_%s.log" % bucket)


def to_syslog(data):
    """
    Writes dictionaries of data generated by an AuditedServerSession to syslog.

    Takes advantage of your system's native logger and writes to wherever
    you have it configured, which is independent of Evennia.
    Linux systems tend to write to /var/log/syslog.

    If you're running rsyslog, you can configure it to dump and/or forward logs
    to disk and/or an external data warehouse (recommended-- if your server is
    compromised or taken down, losing your logs along with it is no help!).

    Args:
        data (dict): Parsed session transmission data.

    """
    # Remove objects before serialization
    data.pop("objects")

    # Write it out
    syslog.syslog(json.dumps(data))
