from resources.lib.globals import *
from .account import Account
from .mlbmonitor import MLBMonitor


def categories(force_date_game_selection=False):
    xbmc.log('THROMER categories auto_select_game: %s, force_date_game_selection: %s' % (AUTO_SELECT_GAME, force_date_game_selection), level=xbmc.LOGINFO)
    if AUTO_SELECT_GAME != '0' and not force_date_game_selection:
        auto_select_game()
        return
    addDir(LOCAL_STRING(30360), 100, ICON, FANART)
    addDir(LOCAL_STRING(30361), 105, ICON, FANART)
    addDir(LOCAL_STRING(30362), 200, ICON, FANART)
    # show Featured Videos in the main menu
    addDir(LOCAL_STRING(30363), 300, ICON, FANART)


def auto_select_game_fallback(msg):
    xbmc.log('auto_select_game_fallback %s' % msg, level=xbmc.LOGINFO)
    dialog = xbmcgui.Dialog()
    dialog.notification('Auto-select game failed', msg, ICON, 5000, False)
    categories(True)

    
def auto_select_game():
    xbmc.log('auto_select_game', level=xbmc.LOGINFO)
    dialog = xbmcgui.Dialog()
    dialog.notification("ted please implement", "not implemented", ICON, 5000, False)
    old_auto_select_game()

    
    # dialog.ok("ted please implement", "not implemented")
    # actually it would be nice do the little alert thing and send back to mode=108 
    # xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
    #sys.exit()
    # TODO if there is no favorite team, fall back on selecting date & game
    # (or maybe selecting just game, for day with most recent games of any
    # flavor)
    # In case we can't find anything fall back on selecting date & game
    # categories(True)


def old_auto_select_game():
    # This does play the game, but there is no escaping it ever ...
    # 'escape' goes back to the beginning
    # Control 55 in window 10025 has been asked to focus, but it can't
    xbmc.log('THROMER old_auto_select_game handle %s argv1 %s' % (addon_handle, sys.argv[1]), level=xbmc.LOGINFO)
    game_day = localToEastern()
    # team_id = getFavTeamId() TODO!
    team_id = '137'
    url = 'https://statsapi.mlb.com/api/v1/schedule?sportId=1&date=%s&teamId=%s' % (game_day, team_id)
    xbmc.log('THROMER %s' % url, level=xbmc.LOGINFO)
    headers = {
        'User-Agent': UA_ANDROID
    }
    r = requests.get(url,headers=headers, verify=VERIFY)
    json_source = r.json()
    xbmc.log('THROMER: %s' % str(json_source))
    xbmc.log('THROMER got resp' ,level=xbmc.LOGINFO)
    if len(json_source['dates']) == 1:
        games = json_source['dates'][0]['games']
        if len(games) != 1:
            auto_select_game_fallback("No games found for today, or possibly a double header.")
            return

    game_pk = str(games[0]['gamePk'])
    xbmc.log('THROMER found %s' % game_pk, level=xbmc.LOGINFO)
    # stream_select(game_pk)
    old_stream_select(game_pk)  # TODO


def old_stream_select(game_pk):
    url = 'https://statsapi.mlb.com/api/v1/game/' + game_pk + '/content'
    headers = {
        'User-Agent': UA_ANDROID
    }
    xbmc.log('THROMER %s' % url, level=xbmc.LOGINFO)
    r = requests.get(url, headers=headers, verify=VERIFY)
    json_source = r.json()
    xbmc.log('THROMER: %s' % str(json_source))
    xbmc.log('THROMER got resp', level=xbmc.LOGINFO)

    epg = json_source['media']['epg'][0]['items']
    content_id = None
    content_map = {}
    for item in epg:
        xbmc.log(str(item))
        media_feed_type = item['mediaFeedType']
        if item['mediaState'] != 'MEDIA_OFF' and (media_feed_type == 'HOME' or media_feed_type == 'AWAY'):
            content_map[item['callLetters']] = item['contentId']

    for k in ['NBCSBA', 'ESPN', 'FOX', 'FS1', 'TBS', 'ESPN2', 'MLBN', 'CBS', 'TNT']:
        if k in content_map:
            content_id = content_map[k]
            break

    if not content_id:
        auto_select_game_fallback("No broadcast not found")
        return

    stream_url = ''
    xbmc.log('THROMER Account()', level=xbmc.LOGINFO)
    account = Account()
    xbmc.log('THROMER get_stream...', level=xbmc.LOGINFO)
    stream_url, headers, more_headers, _ = account.get_stream_with_more_headers_as_map(content_id)
    Authorization = more_headers['Authorization']

    if not '.m3u8' in stream_url:
        auto_select_game_fallback("Unable to play stream, url is %s" %  stream_url)
        return

    xbmc.log('THROMER stream_url %s ' % stream_url)
    xbmc.log('THROMER headers %s ' % str(headers))
    xbmc.log('THROMER more_headers %s ' % str(more_headers))
    extended_url = '%s|Authorization=%s' % (stream_url, Authorization)
    xbmc.log('THROMER extended_url %s ' % str(extended_url))
    xbmc.log('THROMER play', level=xbmc.LOGINFO)                                    play_stream(extended_url, headers)

    return
    
    #  This has nothing to do with anything
    # list_item = xbmcgui.ListItem(label='baseball game')
    # list_item.setProperty('IsPlayable', 'true')
    # list_item.setPath(extended_url)


    # liz=xbmcgui.ListItem('haha name')
    # liz.setArt({'icon': ICON, 'thumb': ICON, 'fanart': FANART})
    # liz.setProperty("IsPlayable", "true")
    # liz.setInfo( type="Video", infoLabels={ "Title": 'haha title' } )
    # # if info is not None:
    # #     liz.setInfo( type="Video", infoLabels=info)
    # # if video_info is not None:
    # #     liz.addStreamInfo('video', video_info)
    # # if audio_info is not None:
    # #     liz.addStreamInfo('audio', audio_info)


    # xbmc.log('THROMER calling addDirectoryItem ...', level=xbmc.LOGINFO)
    # ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),listitem=liz,url=extended_url,isFolder=False)
    # xbmc.log('THROMER ok=%s' % ok, level=xbmc.LOGINFO)
    # xbmcplugin.setContent(addon_handle, 'episodes')

    # return ok


    # infinite loop below
    xbmc.log('THROMER calling play ...', level=xbmc.LOGINFO)
    # This seems like the wrong way to do it ...
    xbmc.Player().play(extended_url, list_item)
    xbmc.log('THROMER HTH', level=xbmc.LOGINFO)


def todays_games(game_day, force_date_game_selection=False):
    xbmc.log('THROMER enter todays_games', level=xbmc.LOGINFO)
    if game_day is None:
        game_day = localToEastern()
    else:
        force_date_game_selection = True
    if AUTO_SELECT_GAME != '0' and not force_date_game_selection:
        auto_select_game()
        return

    settings.setSetting(id='stream_date', value=game_day)

    display_day = stringToDate(game_day, "%Y-%m-%d")
    #url_game_day = display_day.strftime('year_%Y/month_%m/day_%d')
    prev_day = display_day - timedelta(days=1)

    addDir('[B]<< %s[/B]' % LOCAL_STRING(30010), 101, PREV_ICON, FANART, prev_day.strftime("%Y-%m-%d"))

    date_display = '[B][I]' + colorString(display_day.strftime("%A, %m/%d/%Y"), GAMETIME_COLOR) + '[/I][/B]'

    addPlaylist(date_display, str(game_day), 900, ICON, FANART)

    if ONLY_FREE_GAMES != 'true':
        create_big_inning_listitem(game_day)

    #url = 'http://gdx.mlb.com/components/game/mlb/' + url_game_day + '/grid_ce.json'
    url = API_URL + '/api/v1/schedule'
    # url += '?hydrate=broadcasts(all),game(content(all)),probablePitcher,linescore,team,flags'
    url += '?hydrate=game(content(media(epg))),probablePitcher,linescore,team,flags'
    url += '&sportId=1,51'
    url += '&date=' + game_day

    headers = {
        'User-Agent': UA_ANDROID
    }
    xbmc.log(url)
    xbmc.log('THROMER requests.get %s' % url, level=xbmc.LOGINFO)                                                                             
    r = requests.get(url,headers=headers, verify=VERIFY)
    xbmc.log('THROMER requests.got %s' % url, level=xbmc.LOGINFO)                                                                             
    json_source = r.json()

    try:
        for game in json_source['dates'][0]['games']:
            create_game_listitem(game, game_day)
    except Exception as e:
        xbmc.log('error : ' + str(e), level=xbmc.LOGWARNING)

    next_day = display_day + timedelta(days=1)
    addDir('[B]%s >>[/B]' % LOCAL_STRING(30011), 101, NEXT_ICON, FANART, next_day.strftime("%Y-%m-%d"))
    xbmc.log('THROMER exit todays_games', level=xbmc.LOGINFO)


def create_game_listitem(game, game_day):
    #icon = ICON
    icon = 'https://img.mlbstatic.com/mlb-photos/image/upload/ar_167:215,c_crop/fl_relative,l_team:' + str(game['teams']['home']['team']['id']) + ':fill:spot.png,w_1.0,h_1,x_0.5,y_0,fl_no_overflow,e_distort:100p:0:200p:0:200p:100p:0:100p/fl_relative,l_team:' + str(game['teams']['away']['team']['id']) + ':logo:spot:current,w_0.38,x_-0.25,y_-0.16/fl_relative,l_team:' + str(game['teams']['home']['team']['id']) + ':logo:spot:current,w_0.38,x_0.25,y_0.16/w_750/team/' + str(game['teams']['away']['team']['id']) + '/fill/spot.png'
    # http://mlb.mlb.com/mlb/images/devices/ballpark/1920x1080/2681.jpg
    # B&W
    # fanart = 'http://mlb.mlb.com/mlb/images/devices/ballpark/1920x1080/'+game['venue_id']+'.jpg'
    # Color
    # fanart = 'http://www.mlb.com/mlb/images/devices/ballpark/1920x1080/color/' + str(game['venue']['id']) + '.jpg'
    fanart = 'http://cd-images.mlbstatic.com/stadium-backgrounds/color/light-theme/1920x1080/%s.png' % game['venue']['id']


    xbmc.log(str(game['gamePk']))

    if TEAM_NAMES == "0":
        away_team = game['teams']['away']['team']['teamName']
        home_team = game['teams']['home']['team']['teamName']
    else:
        away_team = game['teams']['away']['team']['abbreviation']
        home_team = game['teams']['home']['team']['abbreviation']

    title = away_team + ' at ' + home_team
    title = title
    xbmc.log('THROMER create_game_listitem considering %s' % title, level=xbmc.LOGINFO)

    is_free = False
    if 'content' in game and 'media' in game['content'] and 'freeGame' in game['content']['media']:
        is_free = game['content']['media']['freeGame']

    fav_game = False
    if game['teams']['away']['team']['name'] in FAV_TEAM:
        fav_game = True
        away_team = colorString(away_team, getFavTeamColor())

    if game['teams']['home']['team']['name'] in FAV_TEAM:
        fav_game = True
        home_team = colorString(home_team, getFavTeamColor())

    game_time = ''
    #if game['status']['abstractGameState'] == 'Preview':
    if game['status']['detailedState'].lower() == 'scheduled' or game['status']['detailedState'].lower() == 'pre-game':
        if game['status']['startTimeTBD'] == True:
            game_time = 'TBD'
        else:
            game_time = game['gameDate']
            game_time = stringToDate(game_time, "%Y-%m-%dT%H:%M:%SZ")
            game_time = UTCToLocal(game_time)

            if TIME_FORMAT == '0':
                game_time = game_time.strftime('%I:%M %p').lstrip('0')
            else:
                game_time = game_time.strftime('%H:%M')

        game_time = colorString(game_time, UPCOMING)

    else:
        #game_time = game['status']['abstractGameState']
        game_time = game['status']['detailedState']

        if game_time == 'Final':
            game_time = colorString(game_time, FINAL)

        elif game['status']['abstractGameState'] == 'Live':
            if game['linescore']['isTopInning']:
                # up triangle
                # top_bottom = u"\u25B2"
                top_bottom = "T"
            else:
                # down triangle
                # top_bottom = u"\u25BC"
                top_bottom = "B"

            inning = game['linescore']['currentInningOrdinal']
            game_time = top_bottom + ' ' + inning

            if game['linescore']['currentInning'] >= 9:
                color = CRITICAL
            else:
                color = LIVE

            game_time = colorString(game_time, color)

        else:
            game_time = colorString(game_time, LIVE)

    #event_id = str(game['calendar_event_id'])
    game_pk = game['gamePk']
    #gid = game['id']
    gid = 'junk'

    live_feeds = 0
    archive_feeds = 0
    stream_date = str(game_day)

    desc = ''
    if 'probablePitcher' in game['teams']['away'] and 'fullName' in game['teams']['away']['probablePitcher']:
        desc += game['teams']['away']['probablePitcher']['fullName']
    else:
        desc += 'TBD'
    desc += ' vs. '
    if 'probablePitcher' in game['teams']['home'] and 'fullName' in game['teams']['home']['probablePitcher']:
        desc += game['teams']['home']['probablePitcher']['fullName']
    else:
        desc += 'TBD'
    if 'venue' in game and 'name' in game['venue']:
        desc += ', from ' + game['venue']['name']
    if 'description' in game and game['description'] != "":
        desc += ' (' + game['description'] + ')'
    spoiler = 'True'
    if NO_SPOILERS == '1' or (NO_SPOILERS == '2' and fav_game) or (NO_SPOILERS == '3' and game_day == localToEastern()) or (NO_SPOILERS == '4' and game_day < localToEastern()) or game['status']['abstractGameState'] == 'Preview':
        spoiler = 'False'
        name = game_time + ' ' + away_team + ' at ' + home_team
    else:
        name = game_time + ' ' + away_team
        if 'linescore' in game: name += ' ' + colorString(str(game['linescore']['teams']['away']['runs']), SCORE_COLOR)
        name += ' at ' + home_team
        if 'linescore' in game: name += ' ' + colorString(str(game['linescore']['teams']['home']['runs']), SCORE_COLOR)

        # check flags
        if 'flags' in game:
            if game['flags']['perfectGame'] == True:
                name += ' ' + colorString('(Perfect Game)', CRITICAL)
            elif game['flags']['noHitter'] == True:
                name += ' ' + colorString('(No-Hitter)', CRITICAL)

    if game['doubleHeader'] != 'N':
        name += ' (Game ' + str(game['gameNumber']) + ')'

    name = name
    if fav_game:
        name = '[B]' + name + '[/B]'

    if is_free:
        name = colorString(name, FREE)

    # Get audio/video info
    audio_info, video_info = getAudioVideoInfo()
    # 'duration':length
    info = {'plot': desc, 'tvshowtitle': 'MLB', 'title': title, 'originaltitle': title, 'aired': game_day, 'genre': LOCAL_STRING(700), 'mediatype': 'video'}

    # If set only show free games in the list
    if ONLY_FREE_GAMES == 'true' and not is_free:
        xbmc.log('THROMER create_game_listitem skipping %s' % title, level=xbmc.LOGINFO)
        return
    xbmc.log('THROMER create_game_listitem adding %s' % title, level=xbmc.LOGINFO)
    add_stream(name, title, game_pk, icon, fanart, info, video_info, audio_info, stream_date, spoiler)


# fetch a list of featured videos
def get_video_list(list_url=None):
    # use the Featured on MLB.TV list (included Big Inning) if no list is specified
    if list_url == None:
        list_url = 'https://dapi.cms.mlbinfra.com/v2/content/en-us/sel-mlbtv-featured-svod-video-list'

    headers = {
        'User-Agent': UA_PC,
        'Origin': 'https://www.mlb.com',
        'Referer': 'https://www.mlb.com',
        'Content-Type': 'application/json'
    }
    xbmc.log('THROMER requests.get %s' % list_url, level=xbmc.LOGINFO)                                                                             
    r = requests.get(list_url, headers=headers, verify=VERIFY)
    xbmc.log('THROMER requests.got %s' % list_url, level=xbmc.LOGINFO)                                                                             
    json_source = r.json()
    return json_source


# display a list of featured videos
def featured_videos(featured_video=None):
    # if no list is specified, use the master list of lists
    if featured_video == None:
        featured_video = 'https://mastapi.mobile.mlbinfra.com/api/video/v1/playlist'

    video_list = get_video_list(featured_video)
    if 'items' in video_list:
        for item in video_list['items']:
            #xbmc.log(str(item))
            if 'title' in item:
                title = item['title']
                liz=xbmcgui.ListItem(title)
                liz.setInfo( type="Video", infoLabels={ "Title": title } )

                # check if a video url is provided
                if 'fields' in item:
                    video_url = None
                    if 'playbackScenarios' in item['fields']:
                        for playback in item['fields']['playbackScenarios']:
                            if playback['playback'] == 'hlsCloud':
                                video_url = playback['location']
                                break
                    elif 'url' in item['fields']:
                        video_url = item['fields']['url']
                    if video_url is not None:
                        xbmc.log('video url : ' + video_url)
                        if 'thumbnail' in item and 'thumbnailUrl' in item['thumbnail']:
                            thumbnail = item['thumbnail']['thumbnailUrl']
                            # modify thumnail URL for use as icon and fanart
                            icon = thumbnail.replace('w_250,h_250,c_thumb,g_auto,q_auto,f_jpg', 't_16x9/t_w1080')
                            fanart = thumbnail.replace('w_250,h_250,c_thumb,g_auto,q_auto,f_jpg', 'g_auto,c_fill,ar_16:9,q_60,w_1920/e_gradient_fade:15,x_0.6,b_black')
                        else:
                            icon = ICON
                            fanart = FANART
                        liz.setArt({'icon': icon, 'thumb': icon, 'fanart': fanart})
                        liz.setProperty("IsPlayable", "true")
                        u=sys.argv[0]+"?mode="+str(301)+"&featured_video="+urllib.quote_plus(video_url)+"&name="+urllib.quote_plus(title)
                        isFolder=False
                # if no video url is provided, we assume it is just another list
                else:
                    list_url = item['url']
                    xbmc.log('list url : ' + list_url)
                    if list_url == "":
                        continue
                    u=sys.argv[0]+"?mode="+str(300)+"&featured_video="+urllib.quote_plus(list_url)
                    isFolder=True

                xbmcplugin.addDirectoryItem(handle=addon_handle,url=u,listitem=liz,isFolder=isFolder)
                xbmcplugin.setContent(addon_handle, 'episodes')

        # if it's a long list, display a "Next" link if provided
        if 'pagination' in video_list and 'nextUrl' in video_list['pagination']:
            title = '[B]%s >>[/B]' % LOCAL_STRING(30011)
            liz=xbmcgui.ListItem(title)
            liz.setInfo( type="Video", infoLabels={ "Title": title } )
            list_url = video_list['pagination']['nextUrl']
            if list_url != "":
                u=sys.argv[0]+"?mode="+str(300)+"&featured_video="+urllib.quote_plus(list_url)
                isFolder=True
                xbmcplugin.addDirectoryItem(handle=addon_handle,url=u,listitem=liz,isFolder=isFolder)
                xbmcplugin.setContent(addon_handle, 'episodes')


# display a Big Inning item within a game list
def create_big_inning_listitem(game_day):
    try:
        # check when we last fetched the Big Inning schedule
        today = localToEastern()
        big_inning_date = str(settings.getSetting(id="big_inning_date"))

        # if we've already fetched it today, use the cached schedule
        if big_inning_date == today:
            xbmc.log('Using cached Big Inning schedule')
            big_inning_schedule = json.loads(settings.getSetting(id="big_inning_schedule"))
        # otherwise, fetch a new big inning schedule
        else:
            xbmc.log('Fetching Big Inning schedule')
            settings.setSetting(id='big_inning_date', value=today)
            url = 'https://www.mlb.com/live-stream-games/big-inning'

            headers = {
                'User-Agent': UA_PC,
                'Origin': 'https://www.mlb.com',
                'Referer': 'https://www.mlb.com'
            }
            r = requests.get(url,headers=headers, verify=VERIFY)
            #xbmc.log(r.text)

            # parse the schedule table
            table = re.findall('<td>([^<]*)<\/td>', r.text)
            xbmc.log('Number of fields in Big Inning schedule table: ' + str(len(table)))

            counter = 0
            table_iter = iter(table)
            columns_in_table = 3
            big_inning_schedule = {}
            for field in table_iter:
                date_display = table[counter]
                xbmc.log('Checking date ' + date_display + ' from Big Inning schedule')
                big_inning_date = parse(date_display).strftime('%Y-%m-%d')
                xbmc.log('Formatted date ' + big_inning_date)
                # ignore dates in the past
                if big_inning_date >= today:
                    big_inning_start = str(UTCToLocal(easternToUTC(parse(big_inning_date + ' ' + table[counter+1]))))
                    big_inning_end = str(UTCToLocal(easternToUTC(parse(big_inning_date + ' ' + table[counter+2]))))
                    big_inning_schedule[big_inning_date] = {'start': big_inning_start, 'end': big_inning_end}
                counter = counter + columns_in_table
                for i in range(columns_in_table - 1):
                    next(table_iter, None)
            # save the scraped schedule
            settings.setSetting(id='big_inning_schedule', value=json.dumps(big_inning_schedule))

        if game_day in big_inning_schedule:
            xbmc.log(game_day + ' has a scheduled Big Inning broadcast')
            display_title = LOCAL_STRING(30368)

            big_inning_start = parse(big_inning_schedule[game_day]['start'])
            big_inning_end = parse(big_inning_schedule[game_day]['end'])

            # format the time for display
            game_time = big_inning_start.strftime('%I:%M %p').lstrip('0') + ' - ' + big_inning_end.strftime('%I:%M %p').lstrip('0')
            now = datetime.now()
            if now < big_inning_start:
                game_time = colorString(game_time, UPCOMING)
            elif now > big_inning_end:
                game_time = colorString(game_time, FINAL)
            elif now >= big_inning_start and now <= big_inning_end:
                display_title = LOCAL_STRING(30367) + LOCAL_STRING(30368)
                game_time = colorString(game_time, LIVE)
            name = game_time + ' ' + display_title

            desc = 'MLB Big Inning brings fans all the best action from around the league with live look-ins, breaking highlights and big moments as they happen all season long. Airing seven days a week on MLB.TV.'

            # create the list item
            liz=xbmcgui.ListItem(name)
            liz.setInfo( type="Video", infoLabels={ "Title": display_title, 'plot': desc } )
            liz.setProperty("IsPlayable", "true")
            icon = 'https://img.mlbstatic.com/mlb-images/image/private/ar_16:9,g_auto,q_auto:good,w_372,c_fill,f_jpg/mlb/uwr8vepua4t1fe8uwyki'
            fanart = 'https://img.mlbstatic.com/mlb-images/image/private/g_auto,c_fill,ar_16:9,q_60,w_1920/e_gradient_fade:15,x_0.6,b_black/mlb/uwr8vepua4t1fe8uwyki'
            liz.setArt({'icon': icon, 'thumb': icon, 'fanart': fanart})
            u=sys.argv[0]+"?mode="+str(301)+"&featured_video="+urllib.quote_plus(LOCAL_STRING(30367) + LOCAL_STRING(30368))+"&name="+urllib.quote_plus(LOCAL_STRING(30367) + LOCAL_STRING(30368))
            xbmcplugin.addDirectoryItem(handle=addon_handle,url=u,listitem=liz,isFolder=False)
            xbmcplugin.setContent(addon_handle, 'episodes')
        else:
            xbmc.log(game_day + ' does not have a scheduled Big Inning broadcast')
    except Exception as e:
        xbmc.log('big inning error : ' + str(e))


def stream_select(game_pk, spoiler='True', from_context_menu=False):
    xbmc.log('THROMER enter stream_select addon_handle=%s' % addon_handle, level=xbmc.LOGINFO)
    url = API_URL + '/api/v1/game/' + game_pk + '/content'
    headers = {
        'User-Agent': UA_ANDROID
    }
    xbmc.log('THROMER requests.get %s' % url, level=xbmc.LOGINFO)                                                                             
    r = requests.get(url, headers=headers, verify=VERIFY)
    xbmc.log('THROMER requests.got %s' % url, level=xbmc.LOGINFO)                                                                             

    json_source = r.json()

    selected_content_id = None
    stream_url = ''
    start = '1'
    stream_type = 'video'
    skip_possible = False
    skip_type = 0
    is_live = False
    start_inning = 0
    start_inning_half = 'top'
    dialog = xbmcgui.Dialog()

    # if auto select stream is enabled and not bypassed with context menu item, loop through looking for favorite team's feed or home/national feed, in that order
    if AUTO_SELECT_STREAM == 'true' and from_context_menu == False:
        epg = json_source['media']['epg'][0]['items']
        for item in epg:
            if item['mediaState'] != 'MEDIA_OFF':
                if 'mediaFeedType' in item and item['mediaFeedType'] != 'IN_MARKET_HOME' and item['mediaFeedType'] != 'IN_MARKET_AWAY':
                    if FAV_TEAM != 'None' and 'mediaFeedSubType' in item and item['mediaFeedSubType'] == getFavTeamId():
                        selected_content_id = item['contentId']
                        break
                    elif selected_content_id is None and 'mediaFeedType' in item and (item['mediaFeedType'] == 'HOME' or item['mediaFeedType'] == 'NATIONAL' ):
                        selected_content_id = item['contentId']

    # fallback to manual stream selection if auto is disabled, bypassed, or didn't find anything
    if selected_content_id is None:
        if sys.argv[3] == 'resume:true':
            stream_title = []
            highlight_offset = 0
        else:
            stream_title = [LOCAL_STRING(30391)]
            highlight_offset = 1
        media_state = []
        content_id = []
        # combine tv and radio items
        epg = json_source['media']['epg'][0]['items'] + json_source['media']['epg'][2]['items']
        for item in epg:
            xbmc.log(str(item))
            if item['mediaState'] != 'MEDIA_OFF':
                # tv and radio items use different variables for home/away
                if 'mediaFeedType' in item:
                    media_feed_type = str(item['mediaFeedType'])
                else:
                    media_feed_type = str(item['type'])
                if IN_MARKET != 'Hide' or (media_feed_type != 'IN_MARKET_HOME' and media_feed_type != 'IN_MARKET_AWAY'):
                    title = media_feed_type.title()
                    title = title.replace('_', ' ')
                    if 'mediaFeedType' in item:
                        title += LOCAL_STRING(30392)
                    else:
                        if item['language'] == 'en':
                            title += LOCAL_STRING(30394)
                        elif item['language'] == 'es':
                            title += LOCAL_STRING(30395)
                        title += LOCAL_STRING(30393)
                    if 'mediaFeedType' in item and ('HOME' in title.upper() or 'NATIONAL' in title.upper()):
                        media_state.insert(0, item['mediaState'])
                        content_id.insert(0, item['contentId'])
                        stream_title.insert(highlight_offset, title + " (" + item['callLetters'] + ")")
                    else:
                        media_state.append(item['mediaState'])
                        content_id.append(item['contentId'])
                        stream_title.append(title + " (" + item['callLetters'] + ")")

        # All past games should have highlights
        if len(stream_title) == 0:
            dialog = xbmcgui.Dialog()
            dialog.notification(LOCAL_STRING(30383), LOCAL_STRING(30384), ICON, 5000, False)
            xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
            sys.exit()

        n = dialog.select(LOCAL_STRING(30390), stream_title)
        if n == -1:
            sys.exit()
        elif n > -1 and stream_title[n] != LOCAL_STRING(30391):
            # check if selected stream is a radio stream, which can't play with inputstream adaptive
            if LOCAL_STRING(30393) in stream_title[n]:
                stream_type = 'audio'
            selected_content_id = content_id[n-highlight_offset]

    if selected_content_id is not None:
        account = Account()
        stream_url, headers, broadcast_start = account.get_stream(selected_content_id)
        if sys.argv[3] == 'resume:true':
            spoiler = "True"
            if stream_type == 'video':
                skip_possible = True
        elif epg[0]['mediaState'] == "MEDIA_ON" and CATCH_UP == 'true' and stream_type == 'video' and from_context_menu == False:
            is_live = True
            start_options = [LOCAL_STRING(30397), LOCAL_STRING(30398), LOCAL_STRING(30399)]
            # add inning start options
            for x in range(1, 12):
                start_options.append(LOCAL_STRING(30409) + ' ' + LOCAL_STRING(30407) + ' ' + str(x))
                start_options.append(LOCAL_STRING(30410) + ' ' + LOCAL_STRING(30407) + ' ' + str(x))
            p = dialog.select(LOCAL_STRING(30396), start_options)
            if p == 0:
                listitem = stream_to_listitem(stream_url, headers)
                highlight_select_stream(json_source['highlights']['highlights']['items'], listitem)
                sys.exit()
            elif p == 1 or p > 2:
                spoiler = "False"
                start = broadcast_start
                skip_possible = True
                if p > 2:
                    p = p - 2
                    start_inning = int(round(((p+0.5) / 2), 0))
                    if (p % 2) == 0 and ((p+1) % 2) == 1:
                        start_inning_half = 'bottom'
            elif p == 2:
                spoiler = "True"
            elif p == -1:
                sys.exit()
        # don't offer to start live radio streams from beginning
        elif epg[0]['mediaState'] == "MEDIA_ON" and CATCH_UP == 'true' and stream_type == 'audio' and from_context_menu == False:
            p = dialog.select(LOCAL_STRING(30396), [LOCAL_STRING(30397), LOCAL_STRING(30399)])
            if p == 0:
                listitem = stream_to_listitem(stream_url, headers, 'True', '1', 'audio')
                highlight_select_stream(json_source['highlights']['highlights']['items'], listitem)
                sys.exit()
            elif p == -1:
                sys.exit()
        elif stream_type == 'video' and from_context_menu == False:
            skip_possible = True
            # For archive games, offer to start at inning if catch up is enabled
            if CATCH_UP == 'true':
                start_options = [LOCAL_STRING(30398)]
                # add inning start options
                for x in range(1, 12):
                    start_options.append(LOCAL_STRING(30409) + ' ' + LOCAL_STRING(30407) + ' ' + str(x))
                    start_options.append(LOCAL_STRING(30410) + ' ' + LOCAL_STRING(30407) + ' ' + str(x))
                p = dialog.select(LOCAL_STRING(30396), start_options)
                if p > 0:
                    start_inning = int(round(((p+0.5) / 2), 0))
                    if (p % 2) == 0 and ((p+1) % 2) == 1:
                        start_inning_half = 'bottom'
                elif p == -1:
                    sys.exit()

    if skip_possible == True and ASK_TO_SKIP == 'true' and from_context_menu == False:
        skip_type = dialog.select(LOCAL_STRING(30403), [LOCAL_STRING(30404), LOCAL_STRING(30408), LOCAL_STRING(30405), LOCAL_STRING(30406)])
        if skip_type == -1:
            sys.exit()

    if '.m3u8' in stream_url:
        play_stream(stream_url, headers, spoiler, start, stream_type, skip_type, selected_content_id, game_pk, is_live, start_inning, start_inning_half)

    elif stream_title[n] == LOCAL_STRING(30391):
        highlight_select_stream(json_source['highlights']['highlights']['items'], None, from_context_menu)

    else:
        xbmc.log('THROMER exit stream_select', level=xbmc.LOGINFO) 
        sys.exit()
    xbmc.log('THROMER exit stream_select', level=xbmc.LOGINFO)                              


# select a stream for a featured video
def featured_stream_select(featured_video, name):
    xbmc.log('video select')
    account = Account()
    video_url = None
    # check if our request video is a URL
    if featured_video.startswith('http'):
        video_url = featured_video
    # otherwise assume it is a video title (used to call Big Inning from the schedule)
    else:
        xbmc.log('must search for video url with title')
        video_list = get_video_list()
        if 'items' in video_list:
            for item in video_list['items']:
                #xbmc.log(str(item))
                # live Big Inning title should start with LIVE and contain Big Inning
                if (featured_video == (LOCAL_STRING(30367) + LOCAL_STRING(30368)) and item['title'].startswith('LIVE') and 'Big Inning' in item['title']) or featured_video == item['title']:
                    xbmc.log('found match')
                    video_url = None
                    if 'fields' in item:
                        if 'playbackScenarios' in item['fields']:
                            for playback in item['fields']['playbackScenarios']:
                                if playback['playback'] == 'hlsCloud':
                                    video_url = playback['location']
                                    break
                        elif 'url' in item['fields']:
                            video_url = item['fields']['url']
    if video_url is None:
        xbmc.log('failed to find video URL for featured video')
        sys.exit()

    xbmc.log('video url : ' + video_url)
    video_stream_url = None
    # if it's not a Big Inning stream and it is HLS (M3U8) or MP4, we can simply stream the URL we already have
    if (not name.startswith('LIVE') or (name.startswith('LIVE') and 'Big Inning' not in name)) and (video_url.endswith('.m3u8') or video_url.endswith('.mp4')):
        video_stream_url = video_url
    # otherwise we need to authenticate and get the stream URL
    else:
        xbmc.log('fetching video stream from url')
        # need a special token for Big Inning
        okta_access_token = account.okta_access_token()
        if okta_access_token is None:
            xbmc.log('failed to get necessary okta access token')
            sys.exit()

        headers = {
            'User-Agent': UA_PC,
            'Authorization': 'Bearer ' + okta_access_token,
            'Accept': '*/*',
            'Origin': 'https://www.mlb.com',
            'Referer': 'https://www.mlb.com'
        }
        xbmc.log('THROMER requests.get %s' % video_url, level=xbmc.LOGINFO) 
        r = requests.get(video_url, headers=headers, verify=VERIFY)
        xbmc.log('THROMER requests.got %s' % video_url, level=xbmc.LOGINFO)                                                                               

        text_source = r.text
        #xbmc.log(text_source)

        # sometimes the returned content is already a stream playlist
        if text_source.startswith('#EXTM3U'):
            xbmc.log('video url is already a stream playlist')
            video_stream_url = video_url
        # otherwise it is JSON containing the stream URL
        else:
            json_source = r.json()
            if 'data' in json_source and len(json_source['data']) > 0 and 'value' in json_source['data'][0]:
                video_stream_url = json_source['data'][0]['value']
                xbmc.log('found video stream url : ' + video_stream_url)

    if video_stream_url is not None:
        headers = 'User-Agent=' + UA_PC
        if '.m3u8' in video_stream_url and QUALITY == 'Always Ask':
            video_stream_url = account.get_stream_quality(video_stream_url)
        # known issue warning: on Kodi 18 Leia WITHOUT inputstream adaptive, Big Inning starts at the beginning and can't seek
        # anyone with inputstream adaptive, or Kodi 19+, will not have this problem
        if name.startswith('LIVE') and 'Big Inning' in name and KODI_VERSION < 19 and not xbmc.getCondVisibility('System.HasAddon(inputstream.adaptive)'):
            dialog = xbmcgui.Dialog()
            dialog.ok(LOCAL_STRING(30370), LOCAL_STRING(30369))
        play_stream(video_stream_url, headers)
    else:
        xbmc.log('unable to find stream for featured video')


def list_highlights(game_pk):
    url = API_URL + '/api/v1/game/' + game_pk + '/content'
    headers = {
        'User-Agent': UA_ANDROID
    }
    r = requests.get(url, headers=headers, verify=VERIFY)
    json_source = r.json()

    if 'highlights' in json_source and 'highlights' in json_source['highlights'] and 'items' in json_source['highlights']['highlights'] and len(json_source['highlights']['highlights']['items']) > 0:
        highlights = get_highlights(json_source['highlights']['highlights']['items'])
        if not highlights:
            msg = LOCAL_STRING(30383)
            dialog = xbmcgui.Dialog()
            dialog.notification(LOCAL_STRING(30391), msg, ICON, 5000, False)
            xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
            sys.exit()

        # play all
        liz=xbmcgui.ListItem(LOCAL_STRING(30411))
        liz.setInfo( type="Video", infoLabels={ "Title": LOCAL_STRING(30411) } )
        liz.setProperty("IsPlayable", "true")
        u=sys.argv[0]+"?mode="+str(107)+"&game_pk="+urllib.quote_plus(game_pk)
        isFolder=False

        xbmcplugin.addDirectoryItem(handle=addon_handle,url=u,listitem=liz,isFolder=isFolder)
        xbmcplugin.setContent(addon_handle, 'episodes')

        for clip in highlights:
            liz=xbmcgui.ListItem(clip['title'])
            liz.setInfo( type="Video", infoLabels={ "Title": clip['title'] } )
            liz.setArt({'icon': clip['icon'], 'thumb': clip['icon']})
            liz.setProperty("IsPlayable", "true")
            u=sys.argv[0]+"?mode="+str(301)+"&featured_video="+urllib.quote_plus(clip['url'])+"&name="+urllib.quote_plus(clip['title'])
            isFolder=False

            xbmcplugin.addDirectoryItem(handle=addon_handle,url=u,listitem=liz,isFolder=isFolder)
            xbmcplugin.setContent(addon_handle, 'episodes')


def play_all_highlights_for_game(game_pk):
    url = API_URL + '/api/v1/game/' + game_pk + '/content'
    headers = {
        'User-Agent': UA_ANDROID
    }
    r = requests.get(url, headers=headers, verify=VERIFY)
    json_source = r.json()

    if 'highlights' in json_source and 'highlights' in json_source['highlights'] and 'items' in json_source['highlights']['highlights'] and len(json_source['highlights']['highlights']['items']) > 0:
        highlights = get_highlights(json_source['highlights']['highlights']['items'])
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()

        for clip in highlights:
            listitem = xbmcgui.ListItem(clip['url'])
            listitem.setArt({'icon': clip['icon'], 'thumb': clip['icon'], 'fanart': FANART})
            listitem.setInfo(type="Video", infoLabels={"Title": clip['title']})
            playlist.add(clip['url'], listitem)

        xbmcplugin.setResolvedUrl(handle=addon_handle, succeeded=True, listitem=playlist[0])


def highlight_select_stream(json_source, catchup=None, from_context_menu=False):
    highlights = get_highlights(json_source)
    if not highlights and catchup is None:
        msg = LOCAL_STRING(30383)
        dialog = xbmcgui.Dialog()
        dialog.notification(LOCAL_STRING(30391), msg, ICON, 5000, False)
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
        sys.exit()

    highlight_name = []
    highlight_url = []
    if from_context_menu == False:
        highlight_name.append(LOCAL_STRING(30411))
        highlight_url.append('junk')

    for clip in highlights:
        highlight_name.append(clip['title'])
        highlight_url.append(clip['url'])

    if catchup is None:
        dialog = xbmcgui.Dialog()
        a = dialog.select('Choose Highlight', highlight_name)
    else:
        a = 0

    if a > 0:
        play_stream(highlight_url[a], '')
    elif a == 0:
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()

        for clip in highlights:
            listitem = xbmcgui.ListItem(clip['url'])
            listitem.setArt({'icon': clip['icon'], 'thumb': clip['icon'], 'fanart': FANART})
            listitem.setInfo(type="Video", infoLabels={"Title": clip['title']})
            playlist.add(clip['url'], listitem)

        if catchup is not None:
            playlist.add(catchup.getPath(), catchup)

        xbmcplugin.setResolvedUrl(handle=addon_handle, succeeded=True, listitem=playlist[0])
    elif a == -1:
        sys.exit()


def play_stream(stream_url, headers, spoiler='True', start='1', stream_type='video', skip_type=0, content_id=None, game_pk=None, is_live=False, start_inning=0, start_inning_half='top'):
    xbmc.log('THROMER enter play_stream addon_handle=%s stream_url=%s' % (addon_handle, stream_url), level=xbmc.LOGINFO)
    listitem = stream_to_listitem(stream_url, headers, spoiler, start, stream_type)
    xbmcplugin.setResolvedUrl(handle=addon_handle, succeeded=True, listitem=listitem)
    if skip_type > 0 or start_inning > 0:
        mlbmonitor = MLBMonitor()
        mlbmonitor.skip_monitor(skip_type, content_id, game_pk, is_live, start_inning, start_inning_half)


def get_highlights(items):
    xbmc.log('THROMER enter get_highlights', level=xbmc.LOGINFO) 
    xbmc.log(str(items))
    highlights = []
    for item in sorted(items, key=lambda x: x['date']):
        for playback in item['playbacks']:
            if 'hlsCloud' in playback['name']:
                clip_url = playback['url']
                break
        headline = item['headline']
        icon = item['image']['cuts'][0]['src']
        highlights.append({'url': clip_url, 'title': headline, 'icon': icon})

    return highlights


# Play all recaps or condensed games when a date is selected
def playAllHighlights(stream_date):
    dialog = xbmcgui.Dialog()
    n = dialog.select(LOCAL_STRING(30400), [LOCAL_STRING(30401), LOCAL_STRING(30402)])
    if n == -1:
        sys.exit()

    url = API_URL + '/api/v1/schedule'
    url += '?hydrate=game(content(highlights(highlights)))'
    url += '&sportId=1,51'
    url += '&date=' + stream_date

    headers = {
        'User-Agent': UA_ANDROID
    }
    xbmc.log('THROMER requests.get %s' % url, level=xbmc.LOGINFO)                                                                   
    r = requests.get(url, headers, verify=VERIFY)
    xbmc.log('THROMER requests.got %s' % url, level=xbmc.LOGINFO)                                                                             
    json_source = r.json()

    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    playlist.clear()

    for game in json_source['dates'][0]['games']:
        try:
            fanart = 'http://cd-images.mlbstatic.com/stadium-backgrounds/color/light-theme/1920x1080/%s.png' % game['venue']['id']
            if 'highlights' in game['content']:
                for item in game['content']['highlights']['highlights']['items']:
                    try:
                        title = item['headline']
                        if (n == 0 and title.endswith(' Highlights')) or (n == 1 and item['headline'].startswith('CG: ')):
                            for playback in item['playbacks']:
                                if 'hlsCloud' in playback['name']:
                                    clip_url = playback['url']
                                    break
                            listitem = xbmcgui.ListItem(clip_url)
                            icon = item['image']['cuts'][0]['src']
                            listitem.setArt({'icon': icon, 'thumb': icon, 'fanart': fanart})
                            listitem.setInfo(type="Video", infoLabels={"Title": title})
                            xbmc.log('adding recap to playlist : ' + title)
                            playlist.add(clip_url, listitem)
                    except Exception as e:
                        xbmc.log('error : ' + str(e), level=xbmc.LOGWARNING)
        except Exception as e:
            xbmc.log('error : ' + str(e), level=xbmc.LOGWARNING)

    xbmc.Player().play(playlist)

