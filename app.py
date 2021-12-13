import curses
from dbutil import sqlite_get, sqlite_run, sqlite_get_v2, sqlite_run_v2
from setup import init_db
from menu import get_menu_choice, get_string_from_input
from scrolllist import ScrollList
from utils import debug_info
import time
import dialog


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
		self.m_artists_list = None
		self.m_albums_list = None
		self.m_songs_list = None
		self.m_log_list = None
		self.m_main_curses_window = None
		self.m_artist_num_songs = 0
		self.m_artist_num_albums = 0



	def add_log( self, p_msg ) :
		self.m_log_list.add_item( { 'time' : time.strftime( '%Y-%m-%d %H:%M:%S' ), 'msg' : p_msg } )



	def redraw_title_bar( self ) :
		# Get the size of the screen
		l_scr_size_yx = self.m_main_curses_window.getmaxyx()
		# Get screen width
		l_title_bar_width = l_scr_size_yx[ 1 ] #curses.COLS
		# Prepare a title bar with the title centered
		l_title_bar = self.m_app_title.center( l_title_bar_width ).rjust( l_title_bar_width )
		# Output the bar on first row of the screen
		self.m_main_curses_window.addstr( 0, 0, l_title_bar, curses.A_REVERSE )



	def redraw_status_bar( self, p_status_bar_text ) :
		# Get the size of the screen
		l_scr_size_yx = self.m_main_curses_window.getmaxyx()
		# Get valid status bar width
		l_status_bar_width = l_scr_size_yx[ 1 ] - 1
		# Prepare a string with the text centered
		l_status_bar = p_status_bar_text.center( l_status_bar_width )
		# Output the bar on last row of the screen
		self.m_main_curses_window.addnstr( l_scr_size_yx[ 0 ] - 1, 0, l_status_bar, l_status_bar_width, curses.A_REVERSE )



	def redraw_main_bars( self ) :
		self.redraw_title_bar()
		self.redraw_status_bar( 'F1:Features   ↑/↓:Scroll   ENTER:Activate   TAB:Switch List   F3:Search   F4:Edit   F7:Add   F8:Remove   F10:Quit' )



	def redraw_main_screen( self ) :
		self.redraw_main_bars()
		# try :
		for list_idx, list_obj in enumerate( self.m_lists ) :
			l_selected_bool = list_idx == self.m_selected_list_idx
			if list_idx == self.m_artists_list_idx  : list_obj.redraw_list( l_selected_bool )#, { 'shown_cols_list' : [ 1 ], 'justify_list' : [ 'left' ] } )
			elif list_idx == self.m_albums_list_idx : list_obj.redraw_list( l_selected_bool )#, { 'shown_cols_list' : [ 1, 3, 5, 6 ], 'justify_list' : [ 'left', 'right', 'right', 'right' ] } )
			elif list_idx == self.m_songs_list_idx  : list_obj.redraw_list( l_selected_bool )#, { 'shown_cols_list' : [ 1, 2 ], 'justify_list' : [ 'left', 'right' ] } )
			elif list_idx == self.m_log_list_idx    : list_obj.redraw_list( l_selected_bool )#, { 'shown_cols_list' : [ 0, 1 ], 'justify_list' : [ 'left', 'left' ] } )

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
			self.m_main_curses_window.addnstr( self.m_lists[ self.m_log_list_idx ].m_top_int + 1, 2, f'artists(total): { l_query_result[ 2 ][ 0 ][ "total_artists" ] }', self.m_lists[ 0 ].m_cols_int - 2 )
			self.m_main_curses_window.addnstr( self.m_lists[ self.m_log_list_idx ].m_top_int + 2, 2, f' albums(total): { l_query_result[ 2 ][ 0 ][ "total_albums" ] }', self.m_lists[ 0 ].m_cols_int - 2 )
			self.m_main_curses_window.addnstr( self.m_lists[ self.m_log_list_idx ].m_top_int + 3, 2, f'  songs(total): { l_query_result[ 2 ][ 0 ][ "total_songs" ] }', self.m_lists[ 0 ].m_cols_int - 2 )
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
					SELECT *, MIN( year_released ) AS year
					FROM albums
					'''
					# '''
					# -- Alternative - Returns more then one with same year
					# SELECT albums.*, artists.name AS artist
					# FROM albums, artists
					# WHERE year_released = ( SELECT min( year_released ) AS year_released FROM albums )
					# AND artists.id = albums.artist_id
					# '''
					l_query_result = sqlite_get( self.m_db_file_name, l_sql_query )
					if not l_query_result is None :
						l_msg_box_choices =\
						{
							'choices' :
							[
								[ 'Go back' ]
							],
							'title' : f'''Oldest album: "{ l_query_result[ 2 ][ 0 ][ 'title' ] }" released in { l_query_result[ 2 ][ 0 ][ 'year' ] }'''
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
							'title' : f'''Album with longest playing time: "{ l_query_result[ 2 ][ 0 ][ 'title' ] }" ({ l_query_result[ 2 ][ 0 ][ 'year_released' ] }) length: { l_query_result[ 2 ][ 0 ][ 'total_length' ] }'''
						}
						get_menu_choice( self.m_main_curses_window, l_msg_box_choices )
				case 2 :
					# Get average song length
					l_sql_query =\
					'''
					SELECT CAST( CAST( AVG( songs.duration ) / 60 AS INT) AS STRING ) || ':' || PRINTF( '%02d', AVG( songs.duration ) % 60 ) AS avg_duration
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
							'title' : f'''Average song length: { l_query_result[ 2 ][ 0 ][ 'avg_duration' ] }'''
						}
						get_menu_choice( self.m_main_curses_window, l_msg_box_choices )

		# Return to caller
		return l_features_menu_choice



	def reload_artists( self ) :
		l_sql_query =\
		'''
		SELECT *
		FROM artists
		'''
		l_query_result = sqlite_get( self.m_db_file_name, l_sql_query  )
		self.m_artists_list.empty_list()
		self.m_albums_list.empty_list()
		self.m_songs_list.empty_list()
		for db_row_dict in l_query_result[ 2 ] :
			self.m_artists_list.add_item( db_row_dict )



	def reload_albums_on_artist( self, p_artist_id ) :
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
			self.m_artist_num_songs = l_query_result[ 2 ][ 0 ][ 'artist_songs' ]
		l_sql_query =\
		'''
		SELECT albums.*, CAST( sum( duration ) / 60 AS STRING ) || ':' || PRINTF( '%02d', duration % 60 ) AS length, count( songs.id ) AS songs
		FROM albums
		LEFT JOIN songs
		ON albums.id = songs.album_id
		WHERE albums.artist_id = :artist_id
		GROUP BY albums.id
		'''
		l_query_result = sqlite_get( self.m_db_file_name, l_sql_query, { 'artist_id' : f'{ p_artist_id }' } )
		self.m_artist_num_albums = len( l_query_result[ 2 ] )
		self.m_albums_list.empty_list()
		self.m_songs_list.empty_list()
		for db_row_dict in l_query_result[ 2 ] :
			self.m_albums_list.add_item( db_row_dict )



	def reload_songs_on_album( self, p_album_id ) :
		l_sql_query =\
		"""
		-- Alternative for showing duration as M:S
		SELECT id, title, CAST( duration / 60 AS STRING ) || ':' || PRINTF( '%02d', duration % 60 ) AS duration
		FROM songs
		WHERE songs.album_id = :album_id
		"""
		# Alternative for showing duration as seconds
		# SELECT songs.id, songs.title, songs.duration
		l_query_result = sqlite_get( self.m_db_file_name, l_sql_query, { 'album_id' : f'{ p_album_id }' } )
		self.m_songs_list.empty_list()
		for db_row_dict in l_query_result[ 2 ] :
			self.m_songs_list.add_item( db_row_dict )



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
				for field_itr, field_tuple in enumerate( row.items() ) : table_row_dict |= { field_tuple[ 0 ] : field_tuple[ 1 ] }
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
				for field_itr, field_tuple in enumerate( row.items() ) : table_row_dict |= { field_tuple[ 0 ] : field_tuple[ 1 ] }
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
		WHERE songs.title LIKE :search_string;
		'''
		l_query_result = sqlite_get( self.m_db_file_name, l_sql_query, { 'search_string' : f'%{ l_user_input_str }%' } )
		# For every row from the query append table name and add that row to menu list
		if len( l_query_result[ 2 ] ) > 0 :
			for row in l_query_result[ 2 ] :
				l_new_search_result_item = { 'table_name' : 'songs' }
				table_row_dict = {}
				# As key use column names from l_query_result[ 0 ][ field_itr ]
				#for field_itr, field_val in enumerate( row ) : table_row_dict |= { l_query_result[ 0 ][ field_itr ] : field_val }
				for field_itr, field_tuple in enumerate( row.items() ) : table_row_dict |= { field_tuple[ 0 ] : field_tuple[ 1 ] }
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
					# Select first album in the albums list
					self.m_lists[ self.m_albums_list_idx ].select_first()
					l_selected_album = self.m_lists[ self.m_albums_list_idx ].get_selected_item()
					if l_selected_album is not None :
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



	def add_or_edit_dialog( self, p_add_flag = False ) :
		# For showing the dialog, start with common size
		l_common_dlg_dict = \
		{
			'sizeyx' : [ 22, 70 ]
		}
		# Show different dialog depending on which list has focus
		l_table_name = self.m_lists[ self.m_selected_list_idx ].get_name()
		match l_table_name :
			case 'artists' :
				# For artist
				# 1. name
				# 2. description
				# Init common vars for both edit and add dialog
				l_dlg_title   = ' artist'
				l_name        = ''
				l_description = ''
				# Fill vars with existing values for the edit dialog
				l_selected_artist = self.m_lists[ self.m_artists_list_idx ].get_selected_item()
				if p_add_flag :
					l_dlg_title   = 'Add' + l_dlg_title
				else :
					# Exit if selection requirements are not met
					if l_selected_artist is None :
						return
					l_dlg_title   = 'Edit' + l_dlg_title
					l_name        = ( l_name,        l_selected_artist.get( 'name'        ) )[ bool( l_selected_artist.get( 'name'        ) ) ]
					l_description = ( l_description, l_selected_artist.get( 'description' ) )[ bool( l_selected_artist.get( 'description' ) ) ]
				# Prepare a dict describing the dialog box
				l_dlg_dict = l_common_dlg_dict |\
				{
					'title'    : l_dlg_title,
					'controls' :\
					[
						{
							'name'  : 'name',
							'label' : '       name: ',
							'value' : l_name,
							'lines' : 1,
							'max_length' :  50
						},
						{
							'name'  : 'description',
							'label' : 'description: ',
							'value' : l_description,
							'lines' : 10,
							'max_length' : 500
						}
					]
				}
				# Display an edit dialog box to change the values in the dict
				l_dialog_result = dialog.dialog( self.m_main_curses_window, l_dlg_dict )
				# Prepare a common list of sql params
				l_sql_params =\
				{
					'name'        : dialog.get_value_from_ctl_dict_list( 'name',        l_dlg_dict.get( 'controls' ) ),
					'description' : dialog.get_value_from_ctl_dict_list( 'description', l_dlg_dict.get( 'controls' ) )
				}
				# Values were changed
				if l_dialog_result[ 0 ] and l_dialog_result[ 1 ] :
					# Prepare a sql query
					#l_sql_query = ''
					if p_add_flag :
						# Prepare a sql query for adding new artist
						l_sql_query =\
						f'''
						INSERT INTO
							artists ( name, description )
						VALUES
							( :name, :description )
						'''
					else :
						# Prepare a sql query for editting existing artist
						l_sql_query =\
						f'''
						UPDATE
							artists
						SET
							name = :name,
							description = :description
						WHERE
							id = :id
						'''
						# Add id to the params dict because we are updating an existing row
						l_sql_params |= { 'id' : l_selected_artist.get( 'id' ) }
					# Execute sql query
					db_result = sqlite_run( self.m_db_file_name, l_sql_query, l_sql_params )
					if db_result[ 1 ] > 0 :
						# Database was modified
						if p_add_flag :
							self.add_log( 'Added new artist.' )
						else :
							self.add_log( 'Saved changes of the selected artist.' )
						# Reload artists to show the updated values
						self.reload_artists()
						# Reselect the artist
						self.m_artists_list.select_item_on_dict( { 'id' : l_selected_artist.get( 'id' ) } )

			case 'albums' :
				# For album
				# 1. title
				# 2. description
				# 3. year_released
				# Init common vars for both edit and add dialogs
				l_dlg_title   = ' album'
				l_title       = ''
				l_description = ''
				l_year        = ''
				# Exit if selection requirements are not met
				l_selected_artist = self.m_lists[ self.m_artists_list_idx ].get_selected_item()
				if l_selected_artist is None :
					return
				l_selected_album = self.m_lists[ self.m_albums_list_idx ].get_selected_item()
				# Fill vars with existing values for the edit dialog
				if p_add_flag :
					l_dlg_title   = 'Add' + l_dlg_title
				else :
					if l_selected_album is None :
						return
					l_dlg_title   = 'Edit' + l_dlg_title
					l_title       = ( l_title,       l_selected_album.get( 'title'         ) )[ bool( l_selected_album.get( 'title'         ) ) ]
					l_description = ( l_description, l_selected_album.get( 'description'   ) )[ bool( l_selected_album.get( 'description'   ) ) ]
					l_year        = ( l_year,        l_selected_album.get( 'year_released' ) )[ bool( l_selected_album.get( 'year_released' ) ) ]
				# Prep a dict describing the dialog box
				l_dlg_dict = l_common_dlg_dict |\
				{
					'title'    : l_dlg_title,
					'controls' :\
					[
						{
							'name'  : 'title',
							'label' : '      title: ',
							'value' : l_title,
							'lines' : 1,
							'max_length' :  50
						},
						{
							'name'  : 'description',
							'label' : 'description: ',
							'value' : l_description,
							'lines' : 10,
							'max_length' : 500
						},
						{
							'name'  : 'year_released',
							'label' : '   released: ',
							'value' : l_year,
							'lines' : 1,
							'max_length' : 5
						}
					]
				}
				# Display a dialog that changes the values in the dict
				l_dialog_result = dialog.dialog( self.m_main_curses_window, l_dlg_dict )
				# Prepare a common list of sql params
				l_sql_params =\
				{
					'title'         : dialog.get_value_from_ctl_dict_list( 'title',         l_dlg_dict.get( 'controls' ) ),
					'description'   : dialog.get_value_from_ctl_dict_list( 'description',   l_dlg_dict.get( 'controls' ) ),
					'year_released' : dialog.get_value_from_ctl_dict_list( 'year_released', l_dlg_dict.get( 'controls' ) ),
				}
				# Values were changed
				if l_dialog_result[ 0 ] and l_dialog_result[ 1 ] :
					# Prepare a sql query
					#l_sql_query = ''
					if p_add_flag :
						# Prepare a sql query for adding new artist
						l_sql_query =\
						f'''
						INSERT INTO
							albums ( title, description, year_released, artist_id )
						VALUES
							( :title, :description, :year_released, :artist_id ) 
						'''
						# Add artist_id to the params dict because we are adding a new album
						l_sql_params |= { 'artist_id'     : l_selected_artist.get( 'id' ) }
					else :
						l_sql_query =\
						f'''
						UPDATE
							albums
						SET
							title = :title,
							description = :description,
							year_released = :year_released
						WHERE
							id = :id
						'''
						# Add id to the params dict because we are updating an existing row
						l_sql_params |= { 'id' : l_selected_album.get( 'id' ) }
					# Execute sql query
					db_result = sqlite_run( self.m_db_file_name, l_sql_query, l_sql_params )
					if db_result[ 1 ] > 0 :
						# Database was modified
						if p_add_flag :
							self.add_log( 'Added new album.' )
						else :
							self.add_log( 'Saved changes of the selected album.' )
						# Reload the albums to show the updated values
						self.reload_albums_on_artist( l_selected_artist.get( 'id' ) )
						# Reselect the album in the albums list
						self.m_albums_list.select_item_on_dict( { 'id' : l_selected_album.get( 'id' ) } )
						# Reload the songs to show the updated length
						self.reload_songs_on_album( l_selected_album.get( 'id' ) )

			case 'songs' :
				# For song
				# 1. title
				# 2. duration
				# Init common vars for both edit and add dialog
				l_dlg_title = ' song'
				l_title      = ''
				l_duration  = ''
				l_selected_album = self.m_lists[ self.m_albums_list_idx ].get_selected_item()
				# Exit if selection requirements are not met
				if l_selected_album is None :
					return
				l_selected_song = self.m_lists[ self.m_songs_list_idx ].get_selected_item()
				# Fill vars with existing values for the edit dialog
				if p_add_flag :
					l_dlg_title = 'Add' + l_dlg_title
				else :
					if l_selected_song is None :
						return
					l_sql_query =\
					'''
					SELECT songs.id, songs.title, songs.duration
					FROM songs
					WHERE songs.id = :song_id
					LIMIT 1
					'''
					l_sql_params = { 'song_id' : l_selected_song.get( 'id' ) }
					l_query_result = sqlite_get( self.m_db_file_name, l_sql_query, l_sql_params )
					l_dlg_title = 'Edit' + l_dlg_title
					l_title      = ( l_title,     l_selected_song.get( 'title'     ) )[ bool( l_selected_song.get( 'title'       ) ) ]
					#l_duration  = ( l_duration, l_selected_song.get( 'duration'   ) )[ bool( l_selected_song.get( 'duration'   ) ) ]
					l_duration  = l_query_result[ 2 ][ 0 ][ 'duration' ]
				# Prepare a dict describing the dialog box
				l_dlg_dict = l_common_dlg_dict |\
				{
					'title'    : l_dlg_title,
					'controls' :\
					[
						{
							'name'  : 'title',
							'label' : '   title: ',
							'value' : l_title,
							'lines' : 1,
							'max_length' :  50
						},
						{
							'name'  : 'duration',
							'label' : 'duration: ',
							'value' : l_duration,
							'lines' : 1,
							'max_length' : 4
						}
					]
				}
				# Display an edit dialog that changes the values in the dict
				l_dialog_result = dialog.dialog( self.m_main_curses_window, l_dlg_dict )
				# Prepare a common list of sql params
				l_sql_params =\
				{
					'title'    : dialog.get_value_from_ctl_dict_list( 'title',    l_dlg_dict.get( 'controls' ) ),
					'duration' : dialog.get_value_from_ctl_dict_list( 'duration', l_dlg_dict.get( 'controls' ) ),
					'album_id' : l_selected_album.get( 'id' )
				}
				# Values were changed
				if l_dialog_result[ 0 ] and l_dialog_result[ 1 ] :
					# Prepare a sql query
					#l_sql_query = ''
					if p_add_flag :
						# Prepare a sql query for adding new artist
						l_sql_query =\
						f'''
						INSERT INTO
							songs ( title, duration, album_id )
						VALUES
							( :title, :duration, :album_id )
						'''
						# Add album_id to the params dict because we are adding a new song
						l_sql_params |= { 'album_id'     : l_selected_album.get( 'id' ) }
					else :
						l_sql_query =\
						f'''
						UPDATE
							songs
						SET
							title = :title,
							duration = :duration
						WHERE
							id = :id
						'''
						# Add id to the params dict because we are updating an existing song
						l_sql_params |= { 'id' : l_selected_song.get( 'id' ) }
					# Execute sql query
					db_result = sqlite_run( self.m_db_file_name, l_sql_query, l_sql_params )
					if db_result[ 1 ] > 0 :
						# Database was modified
						if p_add_flag :
							self.add_log( 'Added new song to the album.' )
						else :
							self.add_log( 'Saved changes of the selected song' )
						# Reload the albums to show the updated length
						self.reload_albums_on_artist( l_selected_album.get( 'artist_id' ) )
						# Reselect the album in the albums list
						self.m_albums_list.select_item_on_dict( { 'id' : l_selected_album.get( 'id' ) } )
						# Reload the songs to show the updated length
						self.reload_songs_on_album( l_selected_album.get( 'id' ) )
						# Reselect the song
						self.m_songs_list.select_item_on_dict( { 'id' : l_selected_song.get( 'id' ) } )



	def remove_menu( self ) :
		l_remove_menu_choices =\
		{
			'choices' :
			[
				[ 'No' ],
				[ 'Yes' ]
			],
			'title' : ''
		}
		l_selected_list = self.m_lists[ self.m_selected_list_idx ]
		if l_selected_list is None :
			return
		l_selected_item  = l_selected_list.get_selected_item()
		if l_selected_item is None :
			return
		l_selected_list_name = l_selected_list.get_name()
		# Show different dialog depending on which list has focus
		l_common_sql_query =\
		f'''
		DELETE FROM
			{ l_selected_list_name }
		WHERE
			id = :id
		'''
		l_sql_params = { 'id' : l_selected_item.get( 'id' ) }
		match l_selected_list_name :
			case 'artists' :
				# For artist
				l_remove_menu_choices[ 'title' ] = f'''Really remove the artist: "{ l_selected_item.get( 'name' ) }"? All albums and related songs will also be removed.'''
				l_sql_params |=\
				{
					'name' : l_selected_item.get( 'name' )
				}
			case 'albums' :
				# For album
				l_remove_menu_choices[ 'title' ] = f'''Really remove the album: "{ l_selected_item.get( 'title' ) }"? All related songs will also be removed.'''
				l_sql_params |=\
				{
					'title' : l_selected_item.get( 'title' )
				}
			case 'songs' :
				# For song
				l_remove_menu_choices[ 'title' ] = f'''Really remove the song: "{ l_selected_item.get( 'title' ) }"?'''
				l_sql_params |=\
				{
					'title' : l_selected_item.get( 'title' )
				}
		# Ask the user to confirm
		l_remove_menu_choice = get_menu_choice( self.m_main_curses_window, l_remove_menu_choices )
		# Choice #0 indicates to remove the item
		if l_remove_menu_choice == 1 :
			# Execute sql query
			db_result = sqlite_run_v2( self.m_db_file_name, l_common_sql_query, l_sql_params )
			if db_result[ 'rowcount' ] > 0 :
				# Database was modified
				self.add_log( 'Removed item.' )
				match l_selected_list_name :
					case 'artists' :
						# An artist was removed, reload artists table
						self.reload_artists()
						self.m_artists_list.select_first()
						# Continue load albums of first artist and songs of first album of that artist?
						# l_selected_artist = self.m_artists_list.get_selected_item()
						# if l_selected_artist is None :
						# 	return
						# self.reload_albums_on_artist( l_selected_artist.get( 'id' ) )
						# # Select first album
						# self.m_albums_list.select_first()
						# l_selected_album = self.m_albums_list.get_selected_item()
						# if l_selected_album is None :
						# 	return
						# self.reload_songs_on_album( l_selected_album.get( 'id' ) )
						# self.m_songs_list.select_first()
					case 'albums' :
						# An album was removed, reload albums table
						l_selected_artist = self.m_artists_list.get_selected_item()
						if l_selected_artist is None :
							return
						self.reload_albums_on_artist( l_selected_artist.get( 'id' ) )
						self.m_albums_list.select_first()
						# Continue load albums of first artist and songs of first album of that artist?
						# Select first album
						# l_selected_album = self.m_albums_list.get_selected_item()
						# if l_selected_album is None :
						# 	return
						# self.reload_songs_on_album( l_selected_album.get( 'id' ) )
						# self.m_songs_list.select_first()
					case 'songs' :
						# A song was removed, reload songs table
						l_selected_album = self.m_albums_list.get_selected_item()
						if l_selected_album is None :
							return
						self.reload_songs_on_album( l_selected_album.get( 'id' ) )
						# Select first album ?
						# self.m_songs_list.select_first()



	def run( self, p_stdscr ) :
		# Ensure we have minimum terminal size
		l_scr_hw = [ x for x in p_stdscr.getmaxyx() ]
		if l_scr_hw[ 0 ] <  30 : l_scr_hw[ 0 ] =  30
		if l_scr_hw[ 1 ] < 120 : l_scr_hw[ 1 ] = 120
		curses.resize_term( l_scr_hw[ 0 ], l_scr_hw[ 1 ] )

		self.m_main_curses_window = p_stdscr

		# Hide blinking cursor
		curses.curs_set( 0 )

		# Get the size of the screen
		l_scr_size_yx = self.m_main_curses_window.getmaxyx()
		l_available_screen_height = l_scr_size_yx[ 0 ] - 1 - 1

		# Init database and create tables, if new
		init_db( self.m_db_file_name )

		# Define 4 list boxes for UI
		# Artists list
		l_artists_list_options_dict =\
		{
			'vis_cols_list'   : [ 1 ],
			'col_labels_list' : [ 'Name' ],
			'justify_list'    : [ 'left' ]
		}
		self.m_artists_list = ScrollList( self.m_main_curses_window, 'artists', True, int( l_available_screen_height - 9 ), 25, 1, 0, False, options = l_artists_list_options_dict )
		self.m_lists.append( self.m_artists_list )
		self.m_artists_list_idx = len( self.m_lists ) - 1
		# Albums list
		l_albums_list_options_dict =\
		{
			'vis_cols_list'   : [ 1, 3, 5, 6 ],
			'col_labels_list' : [ 'Title', 'Year', 'Length', 'Songs' ],
			'justify_list'    : [ 'left', 'right', 'right', 'right' ]
		}
		l_available_screen_width = l_scr_size_yx[ 1 ] - self.m_lists[ 0 ].m_left_int - self.m_lists[ 0 ].m_cols_int - 2
		self.m_albums_list = ScrollList( self.m_main_curses_window, 'albums', True, int( l_available_screen_height - 9 ), int( l_available_screen_width / 2 ), 1, self.m_lists[ 0 ].m_left_int + self.m_lists[ 0 ].m_cols_int + 1, False, options = l_albums_list_options_dict )
		self.m_lists.append( self.m_albums_list )
		self.m_albums_list_idx = len( self.m_lists ) - 1
		# Songs list
		l_songs_list_options_dict =\
		{
			'vis_cols_list'   : [ 1, 2 ],
			'col_labels_list' : [ 'Title', 'Length' ],
			'justify_list'    : [ 'left', 'right' ]
		}
		l_available_screen_width = l_scr_size_yx[ 1 ] - self.m_lists[ 1 ].m_left_int - self.m_lists[ 1 ].m_cols_int - 2
		self.m_songs_list = ScrollList( self.m_main_curses_window, 'songs', True, int( l_available_screen_height - 9 ), l_available_screen_width, 1, self.m_lists[ 1 ].m_left_int + self.m_lists[ 1 ].m_cols_int + 1, False, options = l_songs_list_options_dict )
		self.m_lists.append( self.m_songs_list )
		self.m_songs_list_idx = len( self.m_lists ) - 1
		# Logs list
		l_log_list_options_dict =\
		{
			'vis_cols_list'      : [ 1 ],
			'col_labels_list'    : [ 'Message' ],
			'justify_list'       : [ 'left', 'left' ],
			'disabled_keys_list' : [ curses.KEY_ENTER, 13, 10, curses.KEY_F4, curses.KEY_F7, curses.KEY_F8 ]
		}
		l_available_screen_height -= (self.m_lists[ 0 ].m_lines_int + 2 )
		l_available_screen_width = l_scr_size_yx[ 1 ] - self.m_lists[ 0 ].m_left_int - self.m_lists[ 0 ].m_cols_int - 2
		self.m_log_list = ScrollList( self.m_main_curses_window, 'log', False, l_available_screen_height, l_available_screen_width, self.m_lists[ 0 ].m_top_int + self.m_lists[ 0 ].m_lines_int + 1, self.m_lists[ 0 ].m_left_int + self.m_lists[ 0 ].m_cols_int + 1, True, options = l_log_list_options_dict )
		self.m_lists.append( self.m_log_list )
		self.m_log_list_idx = len( self.m_lists ) - 1

		# Add a message to the log
		self.add_log( f'Welcome to { self.m_app_title } { self.m_app_version }.' )
		# Populate UI lists with data from database
		self.reload_artists()
		self.m_lists[ self.m_artists_list_idx ].select_first()
		l_selected_artist = self.m_lists[ self.m_artists_list_idx ].get_selected_item()
		if l_selected_artist is not None :
			# Reload albums that belong to this artist
			self.reload_albums_on_artist( l_selected_artist.get( 'id' ) )
			# Select first album of that artist
			self.m_lists[ self.m_albums_list_idx ].select_first()
			l_selected_album = self.m_lists[ self.m_albums_list_idx ].get_selected_item()
			if l_selected_album is not None :
				# Reload songs that belong to this album
				self.reload_songs_on_album( l_selected_album.get( 'id' ) )
				# # Select first song of that album
				self.m_lists[ self.m_songs_list_idx ].select_first()

		# Define the Quit menu
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
					if not any( x in [ curses.KEY_ENTER, 459, 13, 10 ] for x in self.m_lists[ self.m_selected_list_idx ].m_disabled_keys_list ) :
						match self.m_selected_list_idx :
							case 0 :
								self.add_log( 'Loaded in artist: ' + self.m_lists[ self.m_artists_list_idx ].get_selected_item().get( 'name' ) )
								# Reload albums that belong to this artist
								self.reload_albums_on_artist( self.m_lists[ self.m_artists_list_idx ].get_selected_item().get( 'id' ) )
								if self.m_artist_num_albums > 0 :
									# Select first album of that artist
									self.m_lists[ self.m_albums_list_idx ].select_first()
									# Reload songs that belong to this album
									if self.m_lists[ self.m_albums_list_idx ].get_selected_item() is not None :
										self.reload_songs_on_album( self.m_lists[ self.m_albums_list_idx ].get_selected_item().get( 'id' ) )
										# Select first song of that album
										self.m_lists[ self.m_songs_list_idx ].select_first()
							case 1 :
								self.add_log( 'Loaded in album: ' + self.m_lists[ self.m_albums_list_idx ].get_selected_item().get( 'title' ) )
								# Reload songs that belong to this album
								self.reload_songs_on_album( self.m_lists[ self.m_albums_list_idx ].get_selected_item().get( 'id' ) )
								# Select first song of that album
								self.m_lists[ self.m_songs_list_idx ].select_first()
				case curses.KEY_F1 :
					self.features_dialog()
				case curses.KEY_F3 :
					# The search dialog
					self.search_dialog()
				case curses.KEY_F4 :
					if curses.KEY_F4 not in self.m_lists[ self.m_selected_list_idx ].m_disabled_keys_list :
						self.add_or_edit_dialog() # True == add
				case curses.KEY_F7 :
					# The Add menu
					if curses.KEY_F7 not in self.m_lists[ self.m_selected_list_idx ].m_disabled_keys_list :
						self.add_or_edit_dialog( True )
				case curses.KEY_F8 :
					# The Remove menu
					if curses.KEY_F8 not in self.m_lists[ self.m_selected_list_idx ].m_disabled_keys_list :
						self.remove_menu()
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
