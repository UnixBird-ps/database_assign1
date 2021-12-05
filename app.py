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


	def add_log( self, p_msg ) :
		self.m_lists[ self.m_log_list_idx ].add_item( { 'msg' : p_msg } )


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
					SELECT albums.*, artists.name AS artist
					FROM albums, artists
					WHERE year_released = ( SELECT min( year_released ) AS year_released FROM albums )
					AND artists.id = albums.artist_id
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


	def reload_artists( self ) :
		self.add_log( 'Loading in "Artists".' )
		l_sql_query =\
		'''
		SELECT *
		FROM artists
		'''
		l_query_result = sqlite_get( self.m_db_file_name, l_sql_query  )
		for row_idx, sqlite3_row in enumerate( l_query_result[ 2 ] ) :
			table_row_dict = {}
			# As key use column names from l_query_result[ 0 ][ field_itr ]
			for field_itr, field_val in enumerate( sqlite3_row ) :
				table_row_dict |= { l_query_result[ 0 ][ field_itr ] : field_val }
			self.m_lists[ self.m_artists_list_idx ].add_item( table_row_dict )


	def reload_albums_on_artist( self, p_artist_id ) :
		self.add_log( 'Loading in "Albums".' )
		# Get artist's total number of songs.
		l_sql_query =\
		'''
		SELECT COUNT( DISTINCT songs.id ) AS artist_songs
		FROM songs
		JOIN albums
		ON songs.album_id = albums.id
		AND albums.artist_id = :artist_id
		'''
		l_query_result = sqlite_get( self.m_db_file_name, l_sql_query, { 'artist_id' : f'{ p_artist_id }' } )
		if not l_query_result is None :
			self.m_artist_num_songs = l_query_result[ 2 ][ 0 ][ 0 ]

		# Get all artists
		l_sql_query =\
		'''
		SELECT *
		FROM albums
		WHERE albums.artist_id = :artist_id
		'''
		l_query_result = sqlite_get( self.m_db_file_name, l_sql_query, { 'artist_id' : f'{ p_artist_id }' } )
		self.m_artist_num_albums = len( l_query_result[ 2 ] )
		self.m_lists[ self.m_albums_list_idx ].empty_list()
		for row_idx, sqlite3_row in enumerate( l_query_result[ 2 ] ) :
			table_row_dict = {}
			# As key use column names from l_query_result[ 0 ][ field_itr ]
			for field_itr, field_val in enumerate( sqlite3_row ) :
				table_row_dict |= { l_query_result[ 0 ][ field_itr ] : field_val }
			self.m_lists[ self.m_albums_list_idx ].add_item( table_row_dict )


	def reload_songs_on_album( self, p_album_id ) :
		self.add_log( 'Loading in "Songs".' )
		l_sql_query =\
		"""
		SELECT songs.id, songs.name, CAST( songs.duration / 60 AS STRING ) || ':' || PRINTF( '%02d', songs.duration % 60 ) AS duration
		FROM songs
		WHERE songs.album_id = :album_id
		"""
		l_query_result = sqlite_get( self.m_db_file_name, l_sql_query, { 'album_id' : f'{ p_album_id }' } )
		self.m_lists[ self.m_songs_list_idx ].empty_list()
		for row_idx, sqlite3_row in enumerate( l_query_result[ 2 ] ) :
			table_row_dict = {}
			# As key use column names from l_query_result[ 0 ][ field_itr ]
			for field_itr, field_val in enumerate( sqlite3_row ) :
				table_row_dict |= { l_query_result[ 0 ][ field_itr ] : field_val }
			self.m_lists[ self.m_songs_list_idx ].add_item( table_row_dict )


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
			for row in l_query_result[ 2 ] :
				l_new_search_result_item = { 'table_name' : 'artists' }
				table_row_dict = {}
				# As key use column names from l_query_result[ 0 ][ field_itr ]
				for field_itr, field_val in enumerate( row ) : table_row_dict |= { l_query_result[ 0 ][ field_itr ] : field_val }
				l_new_search_result_item |= { 'table_row' : table_row_dict }
				l_search_results_items.append( l_new_search_result_item )
		# Search in albums
		l_sql_query =\
		'''
		SELECT albums.* -- albums.id, albums.title
		FROM albums
		WHERE albums.title LIKE :search_string;
		'''
		l_query_result = sqlite_get( self.m_db_file_name, l_sql_query, { 'search_string' : f'%{ l_user_input_str }%' } )
		# For every row from the query append table name and add that row to menu list
		if len( l_query_result[ 2 ] ) > 0 :
			for row in l_query_result[ 2 ] :
				l_new_search_result_item = { 'table_name' : 'albums' }
				table_row_dict = {}
				# As key use column names from l_query_result[ 0 ][ field_itr ]
				for field_itr, field_val in enumerate( row ) : table_row_dict |= { l_query_result[ 0 ][ field_itr ] : field_val }
				l_new_search_result_item |= { 'table_row' : table_row_dict }
				l_search_results_items.append( l_new_search_result_item )
		# Search in songs
		l_sql_query =\
		'''
		SELECT songs.*, artists.id AS artist_id
		FROM songs
		JOIN albums, artists
		ON songs.album_id = albums.id
		AND albums.artist_id = artists.id
		WHERE songs.name LIKE :search_string;
		'''
		l_query_result = sqlite_get( self.m_db_file_name, l_sql_query, { 'search_string' : f'%{ l_user_input_str }%' } )
		# For every row from the query append table name and add that row to menu list
		if len( l_query_result[ 2 ] ) > 0 :
			for row in l_query_result[ 2 ] :
				l_new_search_result_item = { 'table_name' : 'songs' }
				table_row_dict = {}
				# As key use column names from l_query_result[ 0 ][ field_itr ]
				for field_itr, field_val in enumerate( row ) : table_row_dict |= { l_query_result[ 0 ][ field_itr ] : field_val }
				l_new_search_result_item |= { 'table_row' : table_row_dict }
				l_search_results_items.append( l_new_search_result_item )

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
			# Insert found items to the choices list, as lists converted from parts of a row dict
			l_table_row = row[ 'table_row' ]
			l_menu_choices[ 'choices' ].insert( max( 0, len( l_menu_choices[ 'choices' ] ) - 1 ), [ row[ 'table_name' ], l_table_row[ list( l_table_row )[ 1 ] ] ] )
		# Wait for user to respond, should return an index of the choice
		l_menu_choice = get_menu_choice(
			self.m_main_curses_window,
			l_menu_choices,
			{
				'selected_int' : 0,                  # Default selected item
				'shown_cols_list' : [ 0, 1 ],        # Indexes of selected fields to display
				'justify_list' : [ 'right', 'left' ] # Alignment of selected fields
			}
		)
		# Return the index, skip if the choice is the last item "Go back"
		if 0 <= l_menu_choice < max( 0, len( l_menu_choices[ 'choices' ] ) - 1 ) :
			self.m_lists[ self.m_albums_list_idx ].empty_list()
			self.m_lists[ self.m_songs_list_idx ].empty_list()
			l_item_to_goto = l_search_results_items[ l_menu_choice ]
			match l_item_to_goto.get( 'table_name' ) :
				case 'artists' :
					# Found item is an artist
					# Select the artist
					self.m_lists[ self.m_artists_list_idx ].select_item_on_dict( { 'id' : l_item_to_goto.get( 'table_row' ).get( 'id' ) } )
					# Reload albums that belongs to this artist
					self.reload_albums_on_artist( l_item_to_goto.get( 'table_row' ).get( 'id' ) )
					# Select first album of that artist
					self.m_lists[ self.m_albums_list_idx ].select_first()
					# Reload songs that belong to this album
					l_album_id = self.m_lists[ self.m_albums_list_idx ].get_selected_item().get( 'id' )
					self.reload_songs_on_album( l_album_id )
					# Select first song of that album
					self.m_lists[ self.m_songs_list_idx ].select_first()
					# Switch current list to artists
					self.m_selected_list_idx = self.m_artists_list_idx
				case 'albums' :
					# Found item is an album
					# Select the artist that owns this album
					self.m_lists[ self.m_artists_list_idx ].select_item_on_dict( { 'id' : l_item_to_goto.get( 'table_row' ).get( 'artist_id' ) } )
					# Reload albums that belongs to this artist
					self.reload_albums_on_artist( l_item_to_goto.get( 'table_row' ).get( 'artist_id' ) )
					# Select the album in the albums list
					self.m_lists[ self.m_albums_list_idx ].select_item_on_dict( { 'id' : l_item_to_goto.get( 'table_row' ).get( 'id' ) } )
					# Reload songs that belongs to this album
					self.reload_songs_on_album( l_item_to_goto.get( 'table_row' ).get( 'album_id' ) )
					# Select first song of that album
					self.m_lists[ self.m_songs_list_idx ].select_first()
					# Switch list to albums
					self.m_selected_list_idx = self.m_albums_list_idx
				case 'songs' :
					# Found item is a song
					# Select the artist that created this song
					self.m_lists[ self.m_artists_list_idx ].select_item_on_dict( { 'id' : l_item_to_goto.get( 'table_row' ).get( 'artist_id' ) } )
					# Reload albums that belong to the artist that owns this song
					self.reload_albums_on_artist( l_item_to_goto.get( 'table_row' ).get( 'artist_id' ) )
					# Select the album in the albums list that this song belongs to
					self.m_lists[ self.m_albums_list_idx ].select_item_on_dict( { 'id' : l_item_to_goto.get( 'table_row' ).get( 'album_id' ) } )
					# Reload songs that belong to this album
					self.reload_songs_on_album( l_item_to_goto.get( 'table_row' ).get( 'album_id' ) )
					# Select that song
					self.m_lists[ self.m_songs_list_idx ].select_item_on_dict( { 'id' : l_item_to_goto.get( 'table_row' ).get( 'id' ) } )
					# Switch list to songs
					self.m_selected_list_idx = self.m_songs_list_idx


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

		# Add a message to the log
		self.add_log( f'Welcome to { self.m_app_title } { self.m_app_version }.' )
		# Populate UI lists with data from database
		self.reload_artists()
		# Select first album of that artist
		self.m_lists[ self.m_artists_list_idx ].select_first()
		# Reload albums that belong to this artist
		self.reload_albums_on_artist( self.m_lists[ self.m_artists_list_idx ].get_selected_item().get( 'id' ) )
		# Select first album of that artist
		self.m_lists[ self.m_albums_list_idx ].select_first()
		# Reload songs that belong to this album
		self.reload_songs_on_album( self.m_lists[ self.m_albums_list_idx ].get_selected_item().get( 'id' ) )
		# # Select first song of that album
		self.m_lists[ self.m_songs_list_idx ].select_first()

		# Create menus
		# l_delete_menu_choices =\
		# {
		# 	'choices' :
		# 	[
		# 		[ 'No' ],
		# 		[ 'Yes' ]
		# 	],
		# 	'title' : 'Really remove? All {1} belonging to this {2} will be removed.'
		# }
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
						#l_selected_data = self.m_lists[ self.m_selected_list_idx ].get_selected_item()
						#if l_selected_data is not None :
							match self.m_selected_list_idx :
								case 0 :
									self.add_log( 'Activated artist: ' + self.m_lists[ self.m_artists_list_idx ].get_selected_item().get( 'name' ) )
									# Reload albums that belong to this artist
									self.reload_albums_on_artist( self.m_lists[ self.m_artists_list_idx ].get_selected_item().get( 'id' ) )
									#self.reload_albums_on_artist( l_selected_data[ list( l_selected_data )[ 0 ] ] )
									# Select first album of that artist
									self.m_lists[ self.m_albums_list_idx ].select_first()
									# Reload songs that belong to this album
									self.reload_songs_on_album( self.m_lists[ self.m_albums_list_idx ].get_selected_item().get( 'id' ) )
									# # Select first song of that album
									self.m_lists[ self.m_songs_list_idx ].select_first()
								case 1 :
									self.add_log( 'Activated album: ' + self.m_lists[ self.m_albums_list_idx ].get_selected_item().get( 'title' ) )
									# Reload songs that belong to this album
									self.reload_songs_on_album( self.m_lists[ self.m_albums_list_idx ].get_selected_item().get( 'id' ) )
									# # Select first song of that album
									self.m_lists[ self.m_songs_list_idx ].select_first()
				case curses.KEY_F1 :
					self.features_dialog()
				case curses.KEY_F3 :
					# The search dialog
					self.search_dialog()
				case curses.KEY_F4 :
					self.edit_dialog()
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
