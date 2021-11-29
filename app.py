import curses
from curses.textpad import rectangle
from dbutil import sqlite_get
from setup import init_db
from menu import get_menu_choice, get_string_from_input
from scrolllist import ScrollList

# Define the app title
_app_title = 'Music database'
l_lists = []
_selected_list = 0
_log_list_id_int = None

def _redraw_title_bar( p_stdscr, p_app_title ) :
	# Get the size of the screen
	l_scr_size_yx = p_stdscr.getmaxyx()
	# Calculate half width and height
	l_center_yx = ( int( l_scr_size_yx[ 0 ] / 2 ), int( l_scr_size_yx[ 1 ] / 2 ) )
	# Get screen width
	l_title_bar_width = curses.COLS
	# Prepare a title bar with the title centered
	l_title_bar = p_app_title.center( l_title_bar_width ).rjust( l_title_bar_width )
	# Output the bar on first row of the screen
	p_stdscr.addstr( 0, 0, l_title_bar, curses.A_REVERSE )


def _redraw_status_bar( p_stdscr, p_right_justified_str ) :
	# Get the size of the screen
	l_scr_size_yx = p_stdscr.getmaxyx()
	# Get screen width
	l_status_bar_width = curses.COLS - 1
	# Prepare a title bar with the title centered
	l_status_bar = p_right_justified_str.rjust( l_status_bar_width )
	# Output the bar on first row of the screen
	p_stdscr.addnstr( l_scr_size_yx[ 0 ] - 1, 0, l_status_bar, curses.COLS - 1, curses.A_REVERSE )


def _redraw_main_bars( p_stdscr ) :
	_redraw_title_bar( p_stdscr, _app_title )
	_redraw_status_bar( p_stdscr, '↑/↓:Scroll Up/Down    ENTER:Activate    TAB:Switch List    F8:Add    Del:Remove    F3:Search    F10:Quit ' )


def _redraw_main_screen( p_stdscr, p_lists = [] ) :
	_redraw_main_bars( p_stdscr )
	# try :
	for item_idx, item in enumerate( p_lists ) :
		l_selected_bool = item_idx == _selected_list
		if item_idx == 0 : item.redraw_list( l_selected_bool, [ 1 ] )
		elif item_idx == 1 : item.redraw_list( l_selected_bool,  [ 1, 2 ] )
		elif item_idx == 2 : item.redraw_list( l_selected_bool,  [ 1, 2 ] )
		else : item.redraw_list( l_selected_bool,  [ 0 ] )

	# except :
	# 	pass


def main( p_stdscr ) :
	global _log_list_id_int

	# Hide blinking cursor
	curses.curs_set( 0 )
	# Enable scrolling
	# p_stdscr.scrollok( True )
	# p_stdscr.idlok( 1 )

	# Define 4 lists for UI: #1 artists, #2 albums, #3 songs, #4 log
	l_available_screen_width = curses.COLS
	l_available_screen_height = curses.LINES - 1 - 1

	#for item in l_lists : print( item )

	db_file_name_str = 'music.sqlite'
	# Init database and create tables, if new
	init_db( db_file_name_str )

	l_lists.append( ScrollList( p_stdscr, 'artists', True, int( l_available_screen_height - 8 ), int( l_available_screen_width / 3 ) - 1, 1, 0, False ) )
	l_available_screen_width -= ( l_lists[ 0 ].m_left_int + l_lists[ 0 ].m_cols_int + 2 )
	l_lists.append( ScrollList( p_stdscr, 'albums' , True, int( l_available_screen_height - 8 ), int( l_available_screen_width / 2 ), 1, l_lists[ 0 ].m_left_int + l_lists[ 0 ].m_cols_int + 1, False ) )
	l_available_screen_width -= ( l_lists[ 1 ].m_cols_int + 1 )
	l_lists.append( ScrollList( p_stdscr, 'songs'  , True, int( l_available_screen_height - 8 ), l_available_screen_width, 1, l_lists[ 1 ].m_left_int + l_lists[ 1 ].m_cols_int + 1, False, [ curses.KEY_ENTER, 13, 10 ] ) )
	l_available_screen_height -= ( l_lists[ 0 ].m_lines_int + 2 )
	l_lists.append( ScrollList( p_stdscr, 'log'    , False, l_available_screen_height, curses.COLS - 1, l_lists[ 0 ].m_top_int + l_lists[ 0 ].m_lines_int + 1, 0, True, [ curses.KEY_ENTER, 13, 10 ] ) )
	_log_list_id_int = len( l_lists ) - 1

	l_lists[ _log_list_id_int ].add_item( [ f'curses.COLORS: { curses.COLORS }' ] )
	l_lists[ _log_list_id_int ].add_item( [ f'curses.COLOR_PAIRS: { curses.COLOR_PAIRS }' ] )

	# Populate UI lists with data from database
	l_lists[ _log_list_id_int ].add_item( [ "Populating 'Artists' list..." ] )
	if len( l_lists ) > 0 :
		query_result = sqlite_get( db_file_name_str, 'SELECT * FROM artists' )
		for row_idx, row in enumerate( query_result[ 2 ] ) :
			l_lists[ 0 ].add_item( row )
	l_lists[ _log_list_id_int ].add_item( [ 'Done' ] )
	# l_lists[ _log_list_id_int ].add_item( [ "Populating 'Albums' list..." ] )
	# if len( l_lists ) > 1 :
	# 	query_result = sqlite_get( db_file_name_str, 'SELECT * FROM albums' )
	# 	for row_idx, row in enumerate( query_result[ 2 ] ) :
	# 		l_lists[ 1 ].add_item( row )
	# l_lists[ _log_list_id_int ].add_item( [ 'Done' ] )
	# l_lists[ _log_list_id_int ].add_item( [ "Populating 'Songs' list..." ] )
	# if len( l_lists ) > 2 :
	# 	query_result = sqlite_get( db_file_name_str, 'SELECT * FROM songs' )
	# 	for row_idx, row in enumerate( query_result[ 2 ] ) :
	# 		l_lists[ 2 ].add_item( row )
	# l_lists[ _log_list_id_int ].add_item( [ 'Done' ] )

	# Create menus
	l_add_menu_choices =\
	{
		'choices':
		[
			'Add artist ...',
			'Add album  ...',
			'Add song   ...',
			'Go back'
		],
		'title' : 'Add music. What to add?'
	}
	l_delete_menu_choices =\
	{
		'choices' :
		[
			'No',
			'Yes'
		],
		'title' : 'Really remove? Items associated with this {} will be removed.'
	}
	l_quit_menu_choices =\
	{
		'choices' :
		[
			'No',
			'Yes'
		],
		'title' : 'Really quit?'
	}

	app_quit_flag = False
	while not app_quit_flag :
		global _selected_list
		p_stdscr.clear()
		_redraw_main_screen( p_stdscr, l_lists )
		#p_stdscr.refresh()
		l_input_key = p_stdscr.getch()
		p_stdscr.addstr( 0, 0, str( l_input_key ) )
		match l_input_key :
			case 9 : # Missing curses.KEY_TAB
				_selected_list += 1
				if _selected_list >= len( l_lists ) : _selected_list = 0
				l_lists[ _selected_list ].m_curses_win_obj.refresh()
			case 351 : # Missing SHIFT + curses.KEY_TAB
				_selected_list -= 1
				if _selected_list < 0 : _selected_list = len( l_lists ) - 1
				if _selected_list < 0 : _selected_list = 0
				l_lists[ _selected_list ].m_curses_win_obj.refresh()
			case curses.KEY_ENTER | 13 | 10 :
				if not any( x in [ curses.KEY_ENTER, 13, 10 ] for x in l_lists[ _selected_list ].m_disabled_keys ) :
					l_lists[ _selected_list ].select_item_pointed()
					l_selected_data = l_lists[ _selected_list ].get_selected_item()
					if l_selected_data is not None: l_lists[ _log_list_id_int ].add_item( [ f'Activated: { l_selected_data[ 1 ] }' ] )

			case curses.KEY_F3 :
				# The search dialog
				#p_stdscr.clear()
				#_redraw_main_bars( p_stdscr )
				l_user_input_str = get_string_from_input( p_stdscr, 'Enter search term' )
				#p_stdscr.addstr( 0, 0, l_user_input_str )
				#p_stdscr.refresh()
			case curses.KEY_F8 :
				# The Add menu
				# p_stdscr.clear()
				#_redraw_main_bars( p_stdscr )
				l_add_menu_choice = get_menu_choice( p_stdscr, l_add_menu_choices )
				#p_stdscr.clear()
			case curses.KEY_F10 :
				# The quit dialog
				p_stdscr.clear()
				_redraw_main_bars( p_stdscr )
				l_quit_menu_choice = get_menu_choice( p_stdscr, l_quit_menu_choices )
				#p_stdscr.clear()
				#_redraw_main_screen( p_stdscr, l_lists )
				match l_quit_menu_choice :
					case 0:
						pass
					case 1 : app_quit_flag = True
			case curses.KEY_UP   : l_lists[ _selected_list ].scroll_rel( -1 )
			case curses.KEY_DOWN : l_lists[ _selected_list ].scroll_rel(  1 )

	# Restore blinking cursor
	curses.curs_set( 1 )
