import evennia
from django.conf import settings

from evennia.accounts.models import AccountDB
from evennia.utils.gametime import gametime


# retrieve game stats
def get_game_stats():
	game_stats = {
		"name": settings.SERVERNAME,
		"summary": settings.GAME_SLOGAN,
		"hostname": settings.SERVER_HOSTNAME if settings.SERVER_HOSTNAME != "localhost" else '',
		"website": f"http://{settings.SERVER_HOSTNAME}" if settings.SERVER_HOSTNAME != "localhost" else '',
	}
	if settings.STAFF_CONTACT_EMAIL:
		game_stats["contact"] = settings.STAFF_CONTACT_EMAIL
	if settings.TELNET_ENABLED:
		game_stats["ports"] = settings.TELNET_PORTS,
	if settings.SSL_ENABLED:
		game_stats["ssl_ports"] = settings.SSL_PORTS,
	if settings.WEBSOCKET_WEBCLIENT_ENABLED and game_stats['website']:
		game_stats["webclient"] = f"{game_stats['website']}/webclient" if game_stats['website'] else ''
	game_stats |= {
	  "players_online": evennia.SESSION_HANDLER.account_count(),
	  "total_players": AccountDB.objects.num_total_accounts() or 0,
	  "uptime": gametime.uptime(),
	}

	if settings.GAME_STATS_DATA:
		# we want the generated data above to take precedence
		game_stats = settings.GAME_STATS_DATA | game_stats
	
	return game_stats
