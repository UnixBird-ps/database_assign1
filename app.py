import curses
from dbutil import sqlite_get
from setup import init_db
from menu import get_menu_choice, get_string_from_input
from scrolllist import ScrollList
from utils import debug_info


class App :

	def __init__( self ) :
		self.m_app_title = 'Music database'
		self.m_app_version = 'version 0.1'
		self.m_db_file_name = 'music.sqlite'
		self.m_lists = []
		self.m_selected_list_idx = 0
		self.m_artists_list_idx = 0
		self.m_albums_list_idx = 1
		self.m_songs_list_idx = 2
		self.m_log_list_idx = 3
		self.m_main_curses_window = None
		self.m_artist_num_songs = 0
		self.m_artist_num_albums = 0


	def redraw_title_bar( self ) :
		# Get the size of the screen
		l_scr_size_yx = self.m_main_curses_window.getmaxyx()
		# Get screen width
		l_title_bar_width = l_scr_size_yx[ 1 ] #curses.COLS
		# Prepare a title bar with the title centered
		l_title_bar = self.m_app_title.center( l_title_bar_width ).rjust( l_title_bar_width )
		# Output the bar on first row of the screen
		self.m_main_curses_window.addstr( 0, 0, l_title_bar, curses.A_REVERSE )


	def redraw_status_bar( self, p_right_justified_str ) :
		# Get the size of the screen
		l_scr_size_yx = self.m_main_curses_window.getmaxyx()
		# Get screen width
		l_status_bar_width = l_scr_size_yx[ 1 ] - 1 #curses.COLS
		# Prepare a title bar with the title centered
		l_status_bar = p_right_justified_str.rjust( l_status_bar_width )
		# Output the bar on first row of the screen
		self.m_main_curses_window.addnstr( l_scr_size_yx[ 0 ] - 1, 0, l_status_bar, l_status_bar_width, curses.A_REVERSE )


	def redraw_main_bars( self ) :
		self.redraw_title_bar()
		self.redraw_status_bar( ' F1:Features   ↑/↓:Scroll   ENTER:Activate   TAB:Switch List   F3:Search   F4:Edit   F7:Add   F8:Remove   F10:Quit ' )


	def redraw_main_screen( self ) :
		self.redraw_main_bars()
		# try :
		for list_idx, list_obj in enumerate( self.m_lists ) :
			l_selected_bool = list_idx == self.m_selected_list_idx
			if list_idx == self.m_artists_list_idx : list_obj.redraw_list( l_selected_bool, { 'shown_cols_list' : [ 1 ], 'justify_list' : [ 'left' ] } )
			elif list_idx == self.m_albums_list_idx : list_obj.redraw_list( l_selected_bool,  { 'shown_cols_list' : [ 1, 3 ], 'justify_list' : [ 'left', 'right' ] } )
			elif list_idx == self.m_songs_list_idx : list_obj.redraw_list( l_selected_bool,  { 'shown_cols_list' : [ 1, 2 ], 'justify_list' : [ 'left', 'right' ] } )
			elif list_idx == self.m_log_list_idx : list_obj.redraw_list( l_selected_bool,  { 'shown_cols_list' : [ 0 ], 'justify_list' : [ 'left' ] } )

		l_sql_query =\
		'''
		SELECT
			count( distinct artists.id ) as total_artists,
			count( distinct albums.id ) as total_albums,
			count( distinct songs.id ) as total_songs
		FROM artists, albums, songs;
		'''
		l_query_result = sqlite_get( self.m_db_file_name, l_sql_query )
		if not l_query_result is None :
			self.m_main_curses_window.addnstr( self.m_lists[ self.m_log_list_idx ].m_top_int + 1, 2, f'artists(total): { l_query_result[ 2 ][ 0 ][ 0 ] }', self.m_lists[ 0 ].m_cols_int - 2 )
			self.m_main_curses_window.addnstr( self.m_lists[ self.m_log_list_idx ].m_top_int + 2, 2, f' albums(total): { l_query_result[ 2 ][ 0 ][ 1 ] }', self.m_lists[ 0 ].m_cols_int - 2 )
			self.m_main_curses_window.addnstr( self.m_lists[ self.m_log_list_idx ].m_top_int + 3, 2, f'  songs(total): { l_query_result[ 2 ][ 0 ][ 2 ] }', self.m_lists[ 0 ].m_cols_int - 2 )
			self.m_main_curses_window.addnstr( self.m_lists[ self.m_log_list_idx ].m_top_int + 4, 2, f' songs(artist): { self.m_artist_num_songs }', self.m_lists[ 0 ].m_cols_int - 2 )
			self.m_main_curses_window.addnstr( self.m_lists[ self.m_log_list_idx ].m_top_int + 5, 2, f'albums(artist): { self.m_artist_num_albums }', self.m_lists[ 0 ].m_cols_int - 2 )
		# except :
		# 	pass


	def reload_artists_table( self ) :
		# Start with empty lists
		# _l_lists[ 0 ].empty_list()
		# l_query_result = sqlite_get( _db_file_name_str, f'SELECT * FROM artists;' )
		# for row_idx, table_row in enumerate( l_query_result[ 2 ] ) :
		# 	_l_lists[ 0 ].add_item( table_row )
		l_artists_selected_item = self.m_lists[ 0 ].get_selected_item()
		self.m_main_curses_window.addnstr( 0, 0, str( l_artists_selected_item ), self.m_main_curses_window.getmaxyx()[ 1 ] )


	def reload_albums_table( self ) :
		self.m_lists[ 1 ].empty_list()
		l_artists_selected_item = self.m_lists[ 0 ].get_selected_item()
		self.m_main_curses_window.addnstr( 0, 0, str( l_artists_selected_item ), self.m_main_curses_window.getmaxyx()[ 1 ] )


	def reload_songs_table( self ) :
		self.m_lists[ 2 ].empty_list()
		l_albums_selected_item = self.m_lists[ 1 ].get_selected_item()
		self.m_main_curses_window.addnstr( 0, 0, str( l_albums_selected_item ), self.m_main_curses_window.getmaxyx()[ 1 ] )


	def features_dialog( self ) :
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
			self.redraw_main_bars()
			l_features_menu_choice = get_menu_choice( self.m_main_curses_window, l_features_menu_choices, { 'selected_int' : l_features_menu_choice } )
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
					l_query_result = sqlite_get( self.m_db_file_name, l_sql_query )
					if not l_query_result is None :
						l_msg_box_choices =\
						{
							'choices' :
							[
								[ 'Go back' ]
							],
							'title' : f'Oldest album: "{ l_query_result[ 2 ][ 0 ][ 1 ] }" released in { l_query_result[ 2 ][ 0 ][ 3 ] }'
						}
						get_menu_choice( self.m_main_curses_window, l_msg_box_choices )
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
					l_query_result = sqlite_get( self.m_db_file_name, l_sql_query )
					if not l_query_result is None :
						l_msg_box_choices =\
						{
							'choices' :
							[
								[ 'Go back' ]
							],
							'title' : f'Album with longest playing time: "{ l_query_result[ 2 ][ 0 ][ 1 ] }" ({ l_query_result[ 2 ][ 0 ][ 2 ] }) length: { l_query_result[ 2 ][ 0 ][ 3 ] }'
						}
						get_menu_choice( self.m_main_curses_window, l_msg_box_choices )
				case 2 :
					# Get average song length
					l_sql_query =\
					'''
						SELECT CAST( CAST( AVG( songs.duration ) / 60 AS INT) AS STRING ) || ':' || PRINTF( '%02d', AVG( songs.duration ) % 60 ) AS average_duration
						FROM songs
					'''
					l_query_result = sqlite_get( self.m_db_file_name, l_sql_query )
					if not l_query_result is None :
						l_msg_box_choices =\
						{
							'choices' :
							[
								[ 'Go back' ]
							],
							'title' : f'Average song length: { l_query_result[ 2 ][ 0 ][ 0 ] }'
						}
						get_menu_choice( self.m_main_curses_window, l_msg_box_choices )

		# Return to caller
		return l_features_menu_choice


	def activate_item_with_id_from_table( self, p_selection_pair_dict ) :
		match p_selection_pair_dict.get( 'table_name' ) :
			case 'artists' :
				# Switch list
				_selected_list = 0
				self.m_lists[ 0 ].select_item_on_dict( p_selection_pair_dict )
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
			case 'albums' :
				# Load artist and album, activate both, switch list to albums, select this album
				# Switch list
				_selected_list = 1
				self.reload_albums_table()
				self.m_lists[ 1 ].select_item_on_dict( p_selection_pair_dict )
				l_albums_selected_item = self.m_lists[ 1 ].get_selected_item()

				#self.m_lists[ self.m_log_list_idx ].add_item( [ str( l_albums_selected_item ) ] )

		# 		l_query_result = sqlite_get( _db_file_name_str, 'SELECT * FROM albums' )
		# 		for row_idx, table_row in enumerate( l_query_result[ 2 ] ) :
		# 			_l_lists[ 1 ].add_item( table_row )
		# 			if p_table_row_id == table_row[ 0 ] : _l_lists[ 1 ].select_item( row_idx )
		# 		l_selected_data = _l_lists[ 1 ].get_selected_item()
				self.m_lists[ 1 ].select_item_on_dict( p_selection_pair_dict )
			case 'songs' :
				# 1. Get the album id of that song
				# 2. Empty songs list and load all songs of that album into songs list
				# 3. Get artist id of that album
				# 4. Empty albums list and load all albums of that artist into albums list
				# 5. Select that album
				# 6. Select that artist
				_selected_list = 2
				self.reload_songs_table( )
				self.m_lists[ _selected_list ].select_item_on_dict( p_selection_pair_dict )


	def search_dialog( self ) :
		# Get search string from user
		l_user_input_str = get_string_from_input( self.m_main_curses_window, 'Search:', 32 )
		# Init empty list
		l_search_results_items = []
		# Search in artists
		l_sql_query =\
		'''
			SELECT * -- artists.id, artists.name
			FROM artists
			WHERE artists.name LIKE :search_string;
		'''
		l_query_result = sqlite_get( self.m_db_file_name, l_sql_query, { 'search_string' : f'%{ l_user_input_str }%' } )
		# For every row from the query append table name and add that row to menu list
		if len( l_query_result[ 2 ] ) > 0 :
			print( str( l_query_result[ 0 ] ) )
			for row in l_query_result[ 2 ] :
				#row_2 = [ itm for itm in row ]
				#row_2.append( 'artists' )

				row_2 = {}
				for field_itr, field_val in enumerate( row ) : row_2 |= { l_query_result[ 0 ][ field_itr ] : field_val }
				row_2 |= { 'table_name' : 'artists' }

				l_search_results_items.append( row_2 )
		# Search in albums
		l_sql_query =\
		'''
			SELECT * -- albums.id, albums.title
			FROM albums
			WHERE albums.title LIKE :search_string;
		'''
		l_query_result = sqlite_get( self.m_db_file_name, l_sql_query, { 'search_string' : f'%{ l_user_input_str }%' } )
		# For every row from the query append table name and add that row to menu list
		if len( l_query_result[ 2 ] ) > 0 :

			#self.m_lists[ self.m_log_list_idx ].add_item( [ str( l_query_result[ 0 ] ) ] )

			for row in l_query_result[ 2 ] :
				#row_2 = [ itm for itm in row ]
				#row_2.append( 'albums' )

				row_2 = {}
				for field_itr, field_val in enumerate( row ) : row_2 |= { l_query_result[ 0 ][ field_itr ] : field_val }
				row_2 |= { 'table_name' : 'albums' }

				l_search_results_items.append( row_2 )
		# Search in songs
		l_sql_query =\
		'''
			SELECT * -- songs.id, songs.name
			FROM songs
			WHERE songs.name LIKE :search_string;
		'''
		l_query_result = sqlite_get( self.m_db_file_name, l_sql_query, { 'search_string' : f'%{ l_user_input_str }%' } )
		# For every row from the query append table name and add that row to menu list
		if len( l_query_result[ 2 ] ) > 0 :

			#self.m_lists[ self.m_log_list_idx ].add_item( [ str( l_query_result[ 0 ] ) ] )

			for row in l_query_result[ 2 ] :
				#row_2 = [ itm for itm in row ]
				#row_2.append( 'songs' )

				row_2 = {}
				for field_itr, field_val in enumerate( row ) : row_2 |= { l_query_result[ 0 ][ field_itr ] : field_val }
				row_2 |= { 'table_name' : 'songs' }

				l_search_results_items.append( row_2 )
		# Create a menu with empty list
		l_menu_choices =\
		{
			'choices' :
			[
				[ 'Go back' ]
			],
			'title' : 'Search results'
		}
		for row in l_search_results_items :
			# Add a row containing table name and row id to the list of choices
			l_menu_choices[ 'choices' ].insert( max( 0, len( l_menu_choices[ 'choices' ] ) - 1 ), { 'name' : row[ list( row )[ 1 ] ], 'table_name' : row[ list( row )[ -1 ] ] } ) #, [ 1, 2 ]
		# Which fields to show in search results
		# Wait for user to respond, should return an index of the choice
		l_menu_choice = get_menu_choice( self.m_main_curses_window, l_menu_choices, { 'selected_int' : 0, 'shown_cols_list' : [ 1, 0 ], 'justify_list' : [ 'right', 'left' ] } )
		if 0 <= l_menu_choice < max( 0, len( l_menu_choices[ 'choices' ] ) - 1 ) :
			# Return a dict
			return l_search_results_items[ l_menu_choice ]


	def run( self, p_stdscr ) :
		self.m_main_curses_window = p_stdscr

		# Hide blinking cursor
		curses.curs_set( 0 )

		# Get the size of the screen
		l_scr_size_yx = self.m_main_curses_window.getmaxyx()
		l_available_screen_width = l_scr_size_yx[ 1 ]
		l_available_screen_height = l_scr_size_yx[ 0 ] - 1 - 1

		# Init database and create tables, if new
		init_db( self.m_db_file_name )

		# Define 4 list boxes for UI
		# Artists list
		self.m_lists.append( ScrollList( self.m_main_curses_window, 'artists', True, int( l_available_screen_height - 8 ), int( l_available_screen_width / 3 ) - 1, 1, 0, False ) )
		self.m_artists_list_idx = len( self.m_lists ) - 1
		# Albums list
		l_available_screen_width = l_scr_size_yx[ 1 ] - self.m_lists[ 0 ].m_left_int - self.m_lists[ 0 ].m_cols_int - 2
		self.m_lists.append( ScrollList( self.m_main_curses_window, 'albums', True, int( l_available_screen_height - 8 ), int( l_available_screen_width / 2 ), 1, self.m_lists[ 0 ].m_left_int + self.m_lists[ 0 ].m_cols_int + 1, False ) )
		self.m_albums_list_idx = len( self.m_lists ) - 1
		# Songs list
		l_available_screen_width = l_scr_size_yx[ 1 ] - self.m_lists[ 1 ].m_left_int - self.m_lists[ 1 ].m_cols_int - 2
		self.m_lists.append( ScrollList( self.m_main_curses_window, 'songs', True, int( l_available_screen_height - 8 ), l_available_screen_width, 1, self.m_lists[ 1 ].m_left_int + self.m_lists[ 1 ].m_cols_int + 1, False, [ curses.KEY_ENTER, 13, 10 ] ) )
		self.m_songs_list_idx = len( self.m_lists ) - 1
		# Logs list
		l_available_screen_height -= (self.m_lists[ 0 ].m_lines_int + 2 )
		l_available_screen_width = l_scr_size_yx[ 1 ] - self.m_lists[ 0 ].m_left_int - self.m_lists[ 0 ].m_cols_int - 2
		self.m_lists.append( ScrollList( self.m_main_curses_window, 'log', False, l_available_screen_height, l_available_screen_width, self.m_lists[ 0 ].m_top_int + self.m_lists[ 0 ].m_lines_int + 1, self.m_lists[ 0 ].m_left_int + self.m_lists[ 0 ].m_cols_int + 1, True, [ curses.KEY_ENTER, 13, 10 ] ) )
		self.m_log_list_idx = len( self.m_lists ) - 1

		self.m_lists[ self.m_log_list_idx ].add_item( [ f'Welcome to { self.m_app_title } { self.m_app_version }.' ] )

		# Populate UI lists with data from database
		self.m_lists[ self.m_log_list_idx ].add_item( [ 'Populating "Artists" list.' ] )
		if len( self.m_lists ) > 0 :
			l_query_result = sqlite_get( self.m_db_file_name, 'SELECT * FROM artists' )
			for row_idx, row in enumerate( l_query_result[ 2 ] ) :
				self.m_lists[ 0 ].add_item( row )

		# Create menus
		l_delete_menu_choices =\
		{
			'choices' :
			[
				[ 'No' ],
				[ 'Yes' ]
			],
			'title' : 'Really remove? All {1} belonging to this {2} will be removed.'
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
			self.m_main_curses_window.clear()
			self.redraw_main_screen()
			l_input_key = self.m_main_curses_window.getch()
			# Act on the key
			match l_input_key :
				case 9 :   # Missing curses.KEY_TAB
					self.m_selected_list_idx += 1
					if self.m_selected_list_idx >= len( self.m_lists ) : self.m_selected_list_idx = 0
					self.m_lists[ self.m_selected_list_idx ].m_curses_win_obj.refresh()
				case 351 : # Missing curses.KEY_TAB + SHIFT
					self.m_selected_list_idx -= 1
					if self.m_selected_list_idx < 0 : self.m_selected_list_idx = len( self.m_lists ) - 1
					if self.m_selected_list_idx < 0 : self.m_selected_list_idx = 0
					self.m_lists[ self.m_selected_list_idx ].m_curses_win_obj.refresh()
				case curses.KEY_ENTER | 459 | 13 | 10 :
					if not any( x in [ curses.KEY_ENTER, 13, 10 ] for x in self.m_lists[ self.m_selected_list_idx ].m_disabled_keys ) and self.m_lists[ self.m_selected_list_idx ].select_item_pointed() :
						l_selected_data = self.m_lists[ self.m_selected_list_idx ].get_selected_item()
						if l_selected_data is not None :
							match self.m_selected_list_idx :
								case 0 :
									self.m_lists[ self.m_log_list_idx ].add_item( [ f'Activated artist: { l_selected_data[ 1 ] }' ] )
									# Get artist's total number of songs.
									l_sql_query =\
									'''
									SELECT COUNT( DISTINCT songs.id ) AS artist_songs
									FROM songs
									JOIN albums
									ON songs.album_id = albums.id
									AND albums.artist_id = :artist_id;
									'''
									l_query_result = sqlite_get( self.m_db_file_name, l_sql_query, { 'artist_id' : f'{ l_selected_data[ 0 ] }' } )
									if not l_query_result is None :
										self.m_artist_num_songs = l_query_result[ 2 ][ 0 ][ 0 ]

									self.m_lists[ self.m_log_list_idx ].add_item( [ 'Populating "Albums" list.' ] )
									l_sql_query =\
									'''
									SELECT albums.*
									FROM albums
									WHERE albums.artist_id = :artist_id;
									'''
									l_query_result = sqlite_get( self.m_db_file_name, l_sql_query, { 'artist_id' : f'{ l_selected_data[ 0 ] }' } )
									self.m_artist_num_albums = len( l_query_result[ 2 ] )
									self.m_lists[ 1 ].empty_list()
									self.m_lists[ 2 ].empty_list()
									for row_idx, row in enumerate( l_query_result[ 2 ] ) : self.m_lists[ 1 ].add_item( row )
								case 1 :
									self.m_lists[ self.m_log_list_idx ].add_item( [ f'Activated album: { l_selected_data[ 1 ] }' ] )
									self.m_lists[ self.m_log_list_idx ].add_item( [ 'Populating "Songs" list.' ] )
									l_sql_query =\
									"""
									SELECT songs.id, songs.name, CAST( songs.duration / 60 AS STRING ) || ':' || PRINTF( '%02d', songs.duration % 60 ) AS duration
									FROM songs
									WHERE songs.album_id = :album_id;
									"""
									l_query_result = sqlite_get( self.m_db_file_name, l_sql_query, { 'album_id' : f'{ l_selected_data[ 0 ] }' } )
									self.m_lists[ 2 ].empty_list()
									for row_idx, row in enumerate( l_query_result[ 2 ] ) : self.m_lists[ 2 ].add_item( row )
				case curses.KEY_F1 :
					self.features_dialog()
				case curses.KEY_F3 :
					# The search dialog
					l_row_id_and_table_name_dict = self.search_dialog()
					if l_row_id_and_table_name_dict is not None :
						self.activate_item_with_id_from_table( l_row_id_and_table_name_dict )
				case curses.KEY_F8 :
					# The Add menu
					pass
				case curses.CTL_DEL :
					# The Remove menu
					pass
				case curses.KEY_F10 :
					# The quit dialog
					self.redraw_main_bars()
					# Ask the user if it is OK to quit
					l_quit_menu_choice = get_menu_choice( self.m_main_curses_window, l_quit_menu_choices )
					if l_quit_menu_choice == 1 : app_quit_flag = True
				case curses.KEY_UP   : self.m_lists[ self.m_selected_list_idx ].scroll_rel( -1 )
				case curses.KEY_DOWN : self.m_lists[ self.m_selected_list_idx ].scroll_rel( 1 )

		# Restore blinking cursor
		curses.curs_set( 1 )
