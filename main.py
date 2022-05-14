from resources.lib.mlb import *

params = get_params()
name = None
mode = None
game_day = None
game_pk = None
gid = None
teams_stream = None
stream_date = None
spoiler = 'True'
featured_video = None

if 'name' in params:
    name = urllib.unquote_plus(params["name"])

if 'mode' in params:
    mode = int(params["mode"])

xbmc.log('THROMER enter main %s' % mode, level=xbmc.LOGINFO)

if 'game_day' in params:
    game_day = urllib.unquote_plus(params["game_day"])

if 'game_pk' in params:
    game_pk = urllib.unquote_plus(params["game_pk"])

if 'teams_stream' in params:
    teams_stream = urllib.unquote_plus(params["teams_stream"])

if 'stream_date' in params:
    stream_date = urllib.unquote_plus(params["stream_date"])

if 'spoiler' in params:
    spoiler = urllib.unquote_plus(params["spoiler"])

if 'featured_video' in params:
    featured_video = urllib.unquote_plus(params["featured_video"])

is_directory = True
cache_directory = True  # default
update_listing = True  # default

xbmc.log('THROMER mode [%s]' % mode, level=xbmc.LOGINFO)
if mode is None:
    xbmc.log('THROMER calling categories', level=xbmc.LOGINFO) 
    categories()

elif mode == 100:
    todays_games(None)
    cache_directory = False  # So that scores, etc. update

elif mode == 101:
    # Prev and Next
    todays_games(game_day)
    # TODO don't cache if game_day is today
    cache_directory = False  # So that scores, etc. update
    update_listing = False  # Subdirectory

# from context menu, use an extra parameter to force manual stream selection
elif mode == 103:
    stream_select(game_pk, spoiler, True)
    is_directory = False

elif mode == 104:
    stream_select(game_pk, spoiler)
    is_directory = False

elif mode == 105:
    # Yesterday's Games
    game_day = localToEastern()
    display_day = stringToDate(game_day, "%Y-%m-%d")
    prev_day = display_day - timedelta(days=1)
    todays_games(prev_day.strftime("%Y-%m-%d"))

# highlights from context menu
elif mode == 106:
    list_highlights(game_pk)
    # TOOD remove. Note: Just fine.

# play all highlights for game from context menu
elif mode == 107:
    play_all_highlights_for_game(game_pk)
    is_directory = False

# force manual date+game selection
elif mode == 108:
    categories(True)

elif mode == 200:
    # Goto Date
    search_txt = ''
    dialog = xbmcgui.Dialog()
    game_day = dialog.input('Enter date (yyyy-mm-dd)', type=xbmcgui.INPUT_ALPHANUM)
    mat = re.match('(\d{4})-(\d{2})-(\d{2})$', game_day)
    if mat is not None:
        todays_games(game_day)
        # TODO don't cache if game_day is today
    else:
        if game_day != '':
            dialog = xbmcgui.Dialog()
            dialog.ok(LOCAL_STRING(30365),LOCAL_STRING(30366))

        xbmc.log('THROMER sys.exit mode %s' % mode, level=xbmc.LOGINFO) 
        sys.exit()

elif mode == 300:
    # Featured Videos.
    featured_videos(featured_video)
    # cache_directory = False  # How cacheable is it? Does it depend?

elif mode == 301:
    featured_stream_select(featured_video, name)
    is_directory = False

elif mode == 400:
    account = Account()
    account.logout()
    dialog = xbmcgui.Dialog()
    dialog.notification(LOCAL_STRING(30260), LOCAL_STRING(30261), ICON, 5000, False)
    is_directory = False

elif mode == 900:
    # play all recaps or condensed games for selected date
    playAllHighlights(stream_date)
    is_directory = False

elif mode == 999:
    xbmc.log('THROMER sys.exit mode %s' % mode, level=xbmc.LOGINFO)
    sys.exit()

if is_directory:
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=cache_directory, updateListing=update_listing)

xbmc.log('THROMER exit main %s' % mode, level=xbmc.LOGINFO)
