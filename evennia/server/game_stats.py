import evennia
from django.conf import settings

from evennia.accounts.models import AccountDB
from evennia.help.filehelp import FILE_HELP_ENTRIES
from evennia.help.models import HelpEntry
from evennia.objects.models import ObjectDB
from evennia.utils.gametime import gametime
from evennia.utils.utils import class_from_module


# retrieve game stats
def get_game_stats():
    game_stats = {
        "name": settings.SERVERNAME,
        "summary": settings.GAME_SLOGAN,
        "hostname": settings.SERVER_HOSTNAME if settings.SERVER_HOSTNAME != "localhost" else '',
        # TODO: this should probably be a setting, like webclient URL - check if it already is
        "website": f"http://{settings.SERVER_HOSTNAME}" if settings.SERVER_HOSTNAME != "localhost" else '',
    }
    if settings.STAFF_CONTACT_EMAIL:
        game_stats["contact"] = settings.STAFF_CONTACT_EMAIL
    if settings.TELNET_ENABLED:
        game_stats["ports"] = settings.TELNET_PORTS,
    if settings.SSL_ENABLED:
        game_stats["ssl_ports"] = settings.SSL_PORTS,
    if settings.WEBSOCKET_WEBCLIENT_ENABLED and game_stats['website']:
        game_stats["webclient"] = f"{game_stats['website']}/webclient"
    game_stats |= {
      "players_online": evennia.SESSION_HANDLER.account_count(),
      "total_players": AccountDB.objects.num_total_accounts() or 0,
      "uptime": gametime.uptime(),
    }

    if settings.GAME_STATS_DATA:
        # we want the generated data above to take precedence
        game_stats = settings.GAME_STATS_DATA | game_stats

    # optionally get additional statistics about the game's database and setup
    enabled_metrics = settings.GAME_STATS_METRICS
    if enabled_metrics.get("objects"):
        Object = class_from_module(
            settings.BASE_OBJECT_TYPECLASS, fallback=settings.FALLBACK_OBJECT_TYPECLASS
        )
        game_stats["objects"] = Object.objects.all_family().count() or 1
    if enabled_metrics.get("rooms"):
        Room = class_from_module(
            settings.BASE_ROOM_TYPECLASS, fallback=settings.FALLBACK_ROOM_TYPECLASS
        )
        game_stats["rooms"] = Room.objects.all_family().count() or 1
    if enabled_metrics.get("helpfiles"):
        # sum all file and db help entries
        game_stats["helpfiles"] = len(FILE_HELP_ENTRIES.all()) + HelpEntry.objects.count()

    return game_stats
