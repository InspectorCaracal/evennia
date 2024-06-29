"""

MSSP - Mud Server Status Protocol

This implements the MSSP telnet protocol as per
http://tintin.sourceforge.net/mssp/.  MSSP allows web portals and
listings to have their crawlers find the mud and automatically
extract relevant information about it, such as genre, how many
active players and so on.


"""

from django.conf import settings

from evennia.server.game_stats import get_game_stats
from evennia.utils import utils

MSSP = bytes([70])  # b"\x46"
MSSP_VAR = bytes([1])  # b"\x01"
MSSP_VAL = bytes([2])  # b"\x02"

# try to get the customized mssp info, if it exists.
#MSSPTable_CUSTOM = utils.variable_from_module(settings.MSSP_META_MODULE, "MSSPTable", default={})

class Mssp:
    """
    Implements the MSSP protocol. Add this to a variable on the telnet
    protocol to set it up.

    """

    def __init__(self, protocol):
        """
        initialize MSSP by storing protocol on ourselves and calling
        the client to see if it supports MSSP.

        Args:
            protocol (Protocol): The active protocol instance.

        """
        self.protocol = protocol
        if settings.MSSP_ENABLED:
            self.protocol.will(MSSP).addCallbacks(self.do_mssp, self.no_mssp)
        else:
            self.protocol.wont(MSSP)

    def no_mssp(self, option):
        """
        Called when mssp is not requested. This is the normal
        operation.

        Args:
            option (Option): Not used.

        """
        self.protocol.handshake_done()

    def do_mssp(self, option):
        """
        Negotiate all the information.

        Args:
            option (Option): Not used.

        """

        game_stats = get_game_stats()

        self.mssp_table = {
            # Required fields
            "NAME": game_stats.pop('name'),
            "PLAYERS": game_stats.pop('players_online'),
            "UPTIME": game_stats.pop('uptime'),
            "PORT": list(
                str(port) for port in reversed(settings.TELNET_PORTS)
            ),  # most important port should be last in list
            # Evennia auto-filled
            "CRAWL DELAY": game_stats.pop("crawl_delay", "-1"),
            "CODEBASE": utils.get_evennia_version(mode="pretty"),
            "FAMILY": "Evennia",
            "ANSI": "1",
            "GMCP": "1" if settings.TELNET_OOB_ENABLED else "0",
            "ATCP": "0",
            "MCCP": "1",
            "MCP": "0",
            "MSDP": "1" if settings.TELNET_OOB_ENABLED else "0",
            "MSP": "0",
            "MXP": "1" if settings.MXP_ENABLED else "0",
            "PUEBLO": "0",
            "SSL": "1" if settings.SSL_ENABLED else "0",
            "UTF-8": "1",
            "ZMP": "0",
            "VT100": "1",
            "XTERM 256 COLORS": "1",
        }

        # auto-generated data should take precedence to custom
        # also, MSSP expects all keys to be capitalized
        self.mssp_table = { key.upper(): val for key, val in game_stats.items() } | self.mssp_table
 
        varlist = b""
        for variable, value in self.mssp_table.items():
            if callable(value):
                value = value()
            if utils.is_iter(value):
                for partval in value:
                    varlist += (
                        MSSP_VAR
                        + bytes(str(variable), "utf-8")
                        + MSSP_VAL
                        + bytes(str(partval), "utf-8")
                    )
            else:
                varlist += (
                    MSSP_VAR + bytes(str(variable), "utf-8") + MSSP_VAL + bytes(str(value), "utf-8")
                )

        # send to crawler by subnegotiation
        self.protocol.requestNegotiation(MSSP, varlist)
        self.protocol.handshake_done()
