import curses
from dbutil import sqlite_get
from setup import init_db
from menu import get_menu_choice, get_string_from_input
from scrolllist import ScrollList

# Define the app title
_app_title = 'Music database'
_app_version = 'version 0.1'
_db_file_name_str = 'music.sqlite'
_l_lists = []
_selected_list = 0
_log_list_id_int = 3
_artist_num_songs = 0
_artist_num_albums = 0

def _redraw_title_bar( p_stdscr, p_app_title ) :
	# Get the size of the screen
	l_scr_size_yx = p_stdscr.getmaxyx()

	# Calculate half width and height
	#l_center_yx = ( int( l_scr_size_yx[ 0 ] / 2 ), int( l_scr_size_yx[ 1 ] / 2 ) )

	# Get screen width
	l_title_bar_width = l_scr_size_yx[ 1 ] #curses.COLS
	# Prepare a title bar with the title centered
	l_title_bar = p_app_title.center( l_title_bar_width ).rjust( l_title_bar_width )
	# Output the bar on first row of the screen
	p_stdscr.addstr( 0, 0, l_title_bar, curses.A_REVERSE )


def _redraw_status_bar( p_stdscr, p_right_justified_str ) :
	# Get the size of the screen
	l_scr_size_yx = p_stdscr.getmaxyx()
	# Get screen width
	l_status_bar_width = l_scr_size_yx[ 1 ] - 1 #curses.COLS
	# Prepare a title bar with the title centered
	l_status_bar = p_right_justified_str.rjust( l_status_bar_width )
	# Output the bar on first row of the screen
	p_stdscr.addnstr( l_scr_size_yx[ 0 ] - 1, 0, l_status_bar, l_status_bar_width, curses.A_REVERSE )


def _redraw_main_bars( p_stdscr ) :
	_redraw_title_bar( p_stdscr, _app_title )
	_redraw_status_bar( p_stdscr, ' F1:Features   ↑/↓:Scroll   ENTER:Activate   TAB:Switch List   F3:Search   F4:Edit   F7:Add   F8:Remove   F10:Quit ' )


def _redraw_main_screen( p_stdscr, p_lists = None ) :
	if p_lists is None : p_lists = []
	_redraw_main_bars( p_stdscr )
	# try :
	for item_idx, item in enumerate( p_lists ) :
		l_selected_bool = item_idx == _selected_list
		if item_idx == 0 : item.redraw_list( l_selected_bool, [ 1 ] )
		elif item_idx == 1 : item.redraw_list( l_selected_bool,  [ 1, 3 ] )
		elif item_idx == 2 : item.redraw_list( l_selected_bool,  [ 1, 2 ] )
		else : item.redraw_list( l_selected_bool,  [ 0 ] )

	l_sql_query =\
	'''
	SELECT
		count( distinct artists.id ) as total_artists,
		count( distinct albums.id ) as total_albums,
		count( distinct songs.id ) as total_songs
	FROM artists, albums, songs;
	'''
	l_query_result = None
	l_query_result = sqlite_get( _db_file_name_str, l_sql_query )
	if not l_query_result is None :
		p_stdscr.addnstr( _l_lists[ _log_list_id_int ].m_top_int + 1, 2, f'artists(total): { l_query_result[ 2 ][ 0 ][ 0 ] }', _l_lists[ 0 ].m_cols_int - 2 )
		p_stdscr.addnstr( _l_lists[ _log_list_id_int ].m_top_int + 2, 2, f' albums(total): { l_query_result[ 2 ][ 0 ][ 1 ] }', _l_lists[ 0 ].m_cols_int - 2 )
		p_stdscr.addnstr( _l_lists[ _log_list_id_int ].m_top_int + 3, 2, f'  songs(total): { l_query_result[ 2 ][ 0 ][ 2 ] }', _l_lists[ 0 ].m_cols_int - 2 )
		p_stdscr.addnstr( _l_lists[ _log_list_id_int ].m_top_int + 4, 2, f' songs(artist): { _artist_num_songs }', _l_lists[ 0 ].m_cols_int - 2 )
		p_stdscr.addnstr( _l_lists[ _log_list_id_int ].m_top_int + 5, 2, f'albums(artist): { _artist_num_albums }', _l_lists[ 0 ].m_cols_int - 2 )
	# except :
	# 	pass


def _reload_tables() :
	# Start with empty lists
	_l_lists[ 0 ].empty_list()
	_l_lists[ 1 ].empty_list()
	_l_lists[ 2 ].empty_list()
	l_query_result = None
	l_query_result = sqlite_get( _db_file_name_str, f'SELECT * FROM artists;' )
	for row_idx, table_row in enumerate( l_query_result[ 2 ] ) :
		_l_lists[ 0 ].add_item( table_row )
	l_query_result = None


def _activate_item_with_id_from_table( p_selection_dict ) :
	global _selected_list
	# match p_table_name :
	# 	case 'artists' :
	# 		# Switch list
	# 		_selected_list = 0
	# 		_reload_tables()
	# 		_l_lists[ 0 ].select_item_on_key( p_selection_dict[ 'id' ], p_selection_dict[ 'table_name' ] )
	# 		l_selected_data = _l_lists[ 0 ].get_selected_item()
	# 		l_sql_query =\
	# 		'''
	# 		SELECT *
	# 		FROM albums
	# 		WHERE albums.artist_id = :artist_id;
	# 		'''
	# 		l_query_result = None
	# 		l_query_result = sqlite_get( _db_file_name_str, l_sql_query, { 'artist_id' : f'{ l_selected_data[ 0 ] }' } )
	# 		for row_idx, table_row in enumerate( l_query_result[ 2 ] ) :
	# 			_l_lists[ 1 ].add_item( table_row )
	# 	case 'albums' :
	# 		# Load artist and album, activate both, switch list to albums, select this album
	# 		# Switch list
	# 		_selected_list = 1
	# 		# Reload tables albums and songs
	# 		_l_lists[ 1 ].empty_list()
	# 		_l_lists[ 2 ].empty_list()
	# 		l_query_result = None
	# 		l_query_result = sqlite_get( _db_file_name_str, 'SELECT * FROM albums' )
	# 		for row_idx, table_row in enumerate( l_query_result[ 2 ] ) :
	# 			_l_lists[ 1 ].add_item( table_row )
	# 			if p_table_row_id == table_row[ 0 ] : _l_lists[ 1 ].select_item( row_idx )
	# 		l_selected_data = _l_lists[ 1 ].get_selected_item()
	#
	# 	case 'songs' :
	# 		# Load artist and album for this song, activate both, switch list to songs, select this song
	# 		_selected_list = 2


def _features_dialog( p_stdscr ) :
	# Create menus
	l_features_menu_choices =\
	{
		'choices' :
		[
			[ 'Oldest album' ],
			[ 'Album with the longest playing time' ],
			[ 'Average song length' ],
			[ 'Go to main screen' ]
		],
		'title' : 'What to show?'
	}
	# Calculate index for last menu item
	l_last_menu_item = len( l_features_menu_choices[ 'choices' ] ) - 1
	#if l_last_menu_item < 0 : l_last_menu_item = 0

	# Loop until last item - 'Go to main screen' is selected
	l_features_menu_choice = -1
	while l_features_menu_choice != l_last_menu_item :
		#p_stdscr.clear()
		_redraw_main_bars( p_stdscr )
		l_features_menu_choice = get_menu_choice( p_stdscr, l_features_menu_choices, l_features_menu_choice )
		match l_features_menu_choice :
			case 0 :
				# Get oldest album
				l_sql_query =\
				'''
					SELECT *, MIN( year_released )
					FROM albums
				'''
				'''
				-- Alternative - Returns more then one with same year
				select albums.*, artists.name as artist
				from albums, artists
				where year_released = ( select min( year_released ) as year_released from albums )
				and artists.id = albums.artist_id
				'''
				l_query_result = None
				l_query_result = sqlite_get( _db_file_name_str, l_sql_query )
				if not l_query_result is None :
					l_msg_box_choices =\
					{
						'choices' :
						[
							[ 'Go back' ]
						],
						'title' : f'Oldest album: "{ l_query_result[ 2 ][ 0 ][ 1 ] }" released in { l_query_result[ 2 ][ 0 ][ 3 ] }'
					}
					get_menu_choice( p_stdscr, l_msg_box_choices )
			case 1 :
				# Get album with longest play length
				l_sql_query =\
				'''
				-- Album with longest playing time.
				SELECT
					albums.id,
					albums.title,
					albums.year_released,
					CAST( sum( songs.duration ) / 60 AS STRING ) || ':' || PRINTF( '%02d', sum( songs.duration ) % 60 ) AS total_length
				FROM albums, songs
				WHERE albums.id = songs.album_id
				GROUP BY songs.album_id
				ORDER BY total_length desc
				LIMIT 1
				'''
				l_query_result = None
				l_query_result = sqlite_get( _db_file_name_str, l_sql_query )
				if not l_query_result is None :
					l_msg_box_choices =\
					{
						'choices' :
						[
							[ 'Go back' ]
						],
						'title' : f'Album with longest playing time: "{ l_query_result[ 2 ][ 0 ][ 1 ] }" ({ l_query_result[ 2 ][ 0 ][ 2 ] }) length: { l_query_result[ 2 ][ 0 ][ 3 ] }'
					}
					get_menu_choice( p_stdscr, l_msg_box_choices )
			case 2 :
				# Get average song length
				l_sql_query =\
				'''
					SELECT CAST( CAST( AVG( songs.duration ) / 60 AS INT) AS STRING ) || ':' || PRINTF( '%02d', AVG( songs.duration ) % 60 ) AS average_duration
					FROM songs
				'''
				l_query_result = None
				l_query_result = sqlite_get( _db_file_name_str, l_sql_query )
				if not l_query_result is None :
					l_msg_box_choices =\
					{
						'choices' :
						[
							[ 'Go back' ]
						],
						'title' : f'Average song length: { l_query_result[ 2 ][ 0 ][ 0 ] }'
					}
					get_menu_choice( p_stdscr, l_msg_box_choices )

	# Return to caller
	return l_features_menu_choice


def _search_dialog( p_stdscr ) :
	# Get search string from user
	l_user_input_str = get_string_from_input( p_stdscr, 'Search:', 32 )
	# Init empty list
	l_menu_list_items = []
	# Search in artists
	l_sql_query =\
	'''
		SELECT artists.id, artists.name
		FROM artists
		WHERE artists.name LIKE :search_string;
	'''
	l_query_result = None
	l_query_result = sqlite_get( _db_file_name_str, l_sql_query, { 'search_string' : f'%{ l_user_input_str }%' } )
	# Add to list
	if len( l_query_result[ 2 ] ) > 0 :
		for row in l_query_result[ 2 ] :
			row_2 = [ itm for itm in row ]
			row_2.append( 'artists' )
			l_menu_list_items.append( row_2 )
	# Search in albums
	l_sql_query =\
	'''
		SELECT albums.id, albums.title
		FROM albums
		WHERE albums.title LIKE :search_string;
	'''
	l_query_result = None
	l_query_result = sqlite_get( _db_file_name_str, l_sql_query, { 'search_string' : f'%{ l_user_input_str }%' } )
	# Add to menu
	if len( l_query_result[ 2 ] ) > 0 :
		for row in l_query_result[ 2 ] :
			row_2 = [ itm for itm in row ]
			row_2.append( 'albums' )
			l_menu_list_items.append( row_2 )
	# Search in songs
	l_sql_query =\
	'''
		SELECT songs.id, songs.name
		FROM songs
		WHERE songs.name LIKE :search_string;
	'''
	l_query_result = None
	l_query_result = sqlite_get( _db_file_name_str, l_sql_query, { 'search_string' : f'%{ l_user_input_str }%' } )
	# Add to menu
	if len( l_query_result[ 2 ] ) > 0 :
		for row in l_query_result[ 2 ] :
			row_2 = [ itm for itm in row ]
			row_2.append( 'songs' )
			l_menu_list_items.append( row_2 )
	# Create a menu with empty list
	l_search_result_choices =\
	{
		'choices' :
		[
			[ 'Go back' ]
		],
		'title' : 'Search results'
	}
	# Specified which fields to show in search results
	for row in l_menu_list_items :
		# Add table
		l_search_result_choices[ 'choices' ].insert( max( 0, len( l_search_result_choices[ 'choices' ] ) - 1 ), [ row[ 2 ], row[ 1 ] ] )
	# Wait for user to respond
	l_search_results_menu_choice = get_menu_choice( p_stdscr, l_search_result_choices )
	if 0 <= l_search_results_menu_choice < max( 0, len( l_search_result_choices[ 'choices' ] ) - 1 ) :
		return l_menu_list_items[ l_search_results_menu_choice ]


def main( p_stdscr ) :
	global _log_list_id_int

	# Hide blinking cursor
	curses.curs_set( 0 )
	# Enable scrolling
	# p_stdscr.scrollok( True )
	# p_stdscr.idlok( 1 )

	# Get the size of the screen
	l_scr_size_yx = p_stdscr.getmaxyx()
	l_available_screen_width = l_scr_size_yx[ 1 ]
	l_available_screen_height = l_scr_size_yx[ 0 ] - 1 - 1

	# Init database and create tables, if new
	init_db( _db_file_name_str )

	# Define 4 list boxes for UI
	# Artists list
	_l_lists.append( ScrollList( p_stdscr, 'artists', True, int( l_available_screen_height - 8 ), int( l_available_screen_width / 3 ) - 1, 1, 0, False ) )
	# Albums list
	l_available_screen_width = l_scr_size_yx[ 1 ] - _l_lists[ 0 ].m_left_int - _l_lists[ 0 ].m_cols_int - 2
	_l_lists.append( ScrollList( p_stdscr, 'albums', True, int( l_available_screen_height - 8 ), int( l_available_screen_width / 2 ), 1, _l_lists[ 0 ].m_left_int + _l_lists[ 0 ].m_cols_int + 1, False ) )
	# Songs list
	l_available_screen_width = l_scr_size_yx[ 1 ] - _l_lists[ 1 ].m_left_int - _l_lists[ 1 ].m_cols_int - 2
	_l_lists.append( ScrollList( p_stdscr, 'songs', True, int( l_available_screen_height - 8 ), l_available_screen_width, 1, _l_lists[ 1 ].m_left_int + _l_lists[ 1 ].m_cols_int + 1, False, [ curses.KEY_ENTER, 13, 10 ] ) )
	# Logs list
	l_available_screen_height -= (_l_lists[ 0 ].m_lines_int + 2 )
	l_available_screen_width = l_scr_size_yx[ 1 ] - _l_lists[ 0 ].m_left_int - _l_lists[ 0 ].m_cols_int - 2
	_l_lists.append( ScrollList( p_stdscr, 'log', False, l_available_screen_height, l_available_screen_width, _l_lists[ 0 ].m_top_int + _l_lists[ 0 ].m_lines_int + 1, _l_lists[ 0 ].m_left_int + _l_lists[ 0 ].m_cols_int + 1, True, [ curses.KEY_ENTER, 13, 10 ] ) )

	_l_lists[ _log_list_id_int ].add_item( [ f'Welcome to { _app_title } { _app_version }.' ] )

	# Populate UI lists with data from database
	_l_lists[ _log_list_id_int ].add_item( [ "Populating 'Artists' list." ] )
	if len( _l_lists ) > 0 :
		l_query_result = None
		l_query_result = sqlite_get( _db_file_name_str, 'SELECT * FROM artists' )
		for row_idx, row in enumerate( l_query_result[ 2 ] ) :
			_l_lists[ 0 ].add_item( row )

	# Create menus
	l_delete_menu_choices =\
	{
		'choices' :
		[
			[ 'No' ],
			[ 'Yes' ]
		],
		'title' : 'Really remove? Items in the lists to the right of associated with this {} will be removed.'
	}
	l_quit_menu_choices =\
	{
		'choices' :
		[
			[ 'No' ],
			[ 'Yes' ]
		],
		'title' : 'Really quit?'
	}

	app_quit_flag = False
	while not app_quit_flag :
		global _selected_list
		global _artist_num_songs
		global _artist_num_albums
		p_stdscr.clear()
		_redraw_main_screen( p_stdscr, _l_lists )
		l_input_key = p_stdscr.getch()
		# Act on the key
		match l_input_key :
			case 9 :   # Missing curses.KEY_TAB
				_selected_list += 1
				if _selected_list >= len( _l_lists ) : _selected_list = 0
				_l_lists[ _selected_list ].m_curses_win_obj.refresh()
			case 351 : # Missing curses.KEY_TAB + SHIFT
				_selected_list -= 1
				if _selected_list < 0 : _selected_list = len( _l_lists ) - 1
				if _selected_list < 0 : _selected_list = 0
				_l_lists[ _selected_list ].m_curses_win_obj.refresh()
			case curses.KEY_ENTER | 459 | 13 | 10 :
				if not any( x in [ curses.KEY_ENTER, 13, 10 ] for x in _l_lists[ _selected_list ].m_disabled_keys ) and _l_lists[ _selected_list ].select_item_pointed() :
					l_selected_data = _l_lists[ _selected_list ].get_selected_item()
					if l_selected_data is not None :
						match _selected_list :
							case 0 :
								_l_lists[ _log_list_id_int ].add_item( [ f'Activated artist: { l_selected_data[ 1 ] }' ] )
								# Get artist's total number of songs.
								l_sql_query =\
								'''
								SELECT COUNT( DISTINCT songs.id ) AS artist_songs
								FROM songs
								JOIN albums
								ON songs.album_id = albums.id
								AND albums.artist_id = :artist_id;
								'''
								l_query_result = None
								l_query_result = sqlite_get( _db_file_name_str, l_sql_query, { 'artist_id' : f'{ l_selected_data[ 0 ] }' } )
								if not l_query_result is None :
									_artist_num_songs = l_query_result[ 2 ][ 0 ][ 0 ]

								_l_lists[ _log_list_id_int ].add_item( [ "Populating 'Albums' list." ] )
								l_sql_query =\
								'''
								SELECT albums.*
								FROM albums
								WHERE albums.artist_id = :artist_id;
								'''
								l_query_result = None
								l_query_result = sqlite_get( _db_file_name_str, l_sql_query, { 'artist_id' : f'{ l_selected_data[ 0 ] }' } )
								_artist_num_albums = len( l_query_result[ 2 ] )
								_l_lists[ 1 ].empty_list()
								_l_lists[ 2 ].empty_list()
								for row_idx, row in enumerate( l_query_result[ 2 ] ) : _l_lists[ 1 ].add_item( row )
							case 1 :
								_l_lists[ _log_list_id_int ].add_item( [ f'Activated album: { l_selected_data[ 1 ] }' ] )
								_l_lists[ _log_list_id_int ].add_item( [ "Populating 'Songs' list." ] )
								l_sql_query =\
								"""
								SELECT songs.id, songs.name, CAST( songs.duration / 60 AS STRING ) || ':' || PRINTF( '%02d', songs.duration % 60 ) AS duration
								FROM songs
								WHERE songs.album_id = :album_id;
								"""
								l_query_result = None
								l_query_result = sqlite_get( _db_file_name_str, l_sql_query, { 'album_id' : f'{ l_selected_data[ 0 ] }' } )
								_l_lists[ 2 ].empty_list()
								for row_idx, row in enumerate( l_query_result[ 2 ] ) : _l_lists[ 2 ].add_item( row )
			case curses.KEY_F1 :
				_features_dialog( p_stdscr )
			case curses.KEY_F3 :
				# The search dialog
				l_return_value = _search_dialog( p_stdscr )
				print( l_return_value )
				if l_return_value is not None :
					#_activate_item_with_id_from_table( l_return_value[ 0 ], l_return_value[ 2 ] )
					_activate_item_with_id_from_table( l_return_value )
			case curses.KEY_F8 :
				# The Add menu
				pass
			case curses.CTL_DEL :
				# The Remove menu
				pass
			case curses.KEY_F10 :
				# The quit dialog
				#p_stdscr.clear()
				_redraw_main_bars( p_stdscr )
				# Ask the user if it is OK to quit
				l_quit_menu_choice = get_menu_choice( p_stdscr, l_quit_menu_choices )
				if l_quit_menu_choice == 1 : app_quit_flag = True
			case curses.KEY_UP   : _l_lists[ _selected_list ].scroll_rel( -1 )
			case curses.KEY_DOWN : _l_lists[ _selected_list ].scroll_rel( 1 )

	# Restore blinking cursor
	curses.curs_set( 1 )
