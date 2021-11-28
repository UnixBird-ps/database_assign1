import curses
from curses.textpad import rectangle
from dbutil import sqlite_get
from setup import init_db
from menu import get_menu_choice, get_string_from_input
from scrolllist import ScrollList

# Define the app title
_app_title = 'Music database'
_selected_list = 0

def _redraw_title_bar( p_stdscr, p_app_title ) :
	# Get the size of the screen
	l_scr_size_yx = p_stdscr.getmaxyx()
	# Calculate half width and height
	l_center_yx = ( int( l_scr_size_yx[ 0 ] / 2 ), int( l_scr_size_yx[ 1 ] / 2 ) )
	# Get screen width
	l_title_bar_width = curses.COLS
	# Prepare a title bar with the title centered
	l_title_bar = p_app_title.center( l_title_bar_width )
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
	p_stdscr.addstr( l_scr_size_yx[ 0 ] - 1, 0, l_status_bar, curses.A_REVERSE )


def _redraw_main_bars( p_stdscr ) :
	_redraw_title_bar( p_stdscr, _app_title )
	_redraw_status_bar( p_stdscr, str( _selected_list ) + '    ↑:Scroll Up    ↓:Scroll Down    TAB:Switch List    F8:Add    F3:Search    F10:Quit ' )


def _redraw_main_screen( p_stdscr, p_lists = [] ) :
	_redraw_main_bars( p_stdscr )
	# try :
	for item in p_lists :
		rectangle(
			p_stdscr,
			item.m_top_int, item.m_left_int,
			item.m_top_int + item.m_height_int, item.m_left_int + item.m_width_int
		)
		item.redraw_list()
	# except :
	# 	pass


def main( p_stdscr ) :
	# Hide blinking cursor
	curses.curs_set( 0 )
	# Enable scrolling
	# p_stdscr.scrollok( True )
	# p_stdscr.idlok( 1 )

	# Define 4 lists for UI: #1 artists, #2 albums, #3 songs, #4 log
	l_available_screen_width = curses.COLS
	l_available_screen_height = curses.LINES - 3
	l_lists = []
	# l_lists.append(
	# 	{
	# 		'name' : 'artists',
	# 		'editable' : True,
	# 		'items' : [],
	# 		'selected_item' : 0,
	# 		'top' : 1,
	# 		'left' : 0,
	# 		'height' : int( l_available_screen_height * 0.75 ),
	# 		'width' : int( l_available_screen_width / 3 ) - 1,
	# 		'curses_win' : curses.window
	# 	}
	# )
	# l_available_screen_width -= ( l_lists[ 0 ][ 'left' ] + l_lists[ 0 ][ 'width' ] + 1 )
	# l_lists.append(
	# 	{
	# 		'name' : 'albums',
	# 		'editable' : True,
	# 		'items' : [],
	# 		'selected_item' : 0,
	# 		'top' : 1,
	# 		'left' : l_lists[ 0 ][ 'left' ] + l_lists[ 0 ][ 'width' ] + 1,
	# 		'height' : int( l_available_screen_height * 0.75 ),
	# 		'width' : int( l_available_screen_width / 2 ) - 1,
	# 		'curses_win' : curses.window
	# 	}
	# )
	# l_available_screen_width -= ( l_lists[ 1 ][ 'width' ] + 1 )
	# l_lists.append(
	# 	{
	# 		'name' : 'songs',
	# 		'editable' : True,
	# 		'items' : [],
	# 		'selected_item' : 0,
	# 		'top' : 1,
	# 		'left' : l_lists[ 1 ][ 'left' ] + l_lists[ 1 ][ 'width' ] + 1,
	# 		'height' : int( l_available_screen_height * 0.75 ),
	# 		'width' : l_available_screen_width - 1,
	# 		'curses_win' : curses.window
	# 	}
	# )
	# l_available_screen_height -= ( l_lists[ 0 ][ 'height' ] + 1 )
	# l_lists.append(
	# 	{
	# 		'name' : 'log',
	# 		'editable' : False,
	# 		'items' : [],
	# 		'selected_item' : 0,
	# 		'top' : l_lists[ 0 ][ 'top' ] + l_lists[ 0 ][ 'height' ] + 1,
	# 		'left' : 0,
	# 		'height' : l_available_screen_height,
	# 		'width' : curses.COLS - 1,
	# 		'curses_win' : curses.window
	# 	}
	# )
	# l_lists[ 0 ][ 'curses_win' ] = curses.newwin( l_lists[ 0 ][ 'height' ], l_lists[ 0 ][ 'width' ], l_lists[ 0 ][ 'top' ], l_lists[ 0 ][ 'left' ] )
	# l_lists[ 1 ][ 'curses_win' ] = curses.newwin( l_lists[ 1 ][ 'height' ], l_lists[ 1 ][ 'width' ], l_lists[ 1 ][ 'top' ], l_lists[ 1 ][ 'left' ] )
	# l_lists[ 2 ][ 'curses_win' ] = curses.newwin( l_lists[ 2 ][ 'height' ], l_lists[ 2 ][ 'width' ], l_lists[ 2 ][ 'top' ], l_lists[ 2 ][ 'left' ] )
	# l_lists[ 3 ][ 'curses_win' ] = curses.newwin( l_lists[ 3 ][ 'height' ], l_lists[ 3 ][ 'width' ], l_lists[ 3 ][ 'top' ], l_lists[ 3 ][ 'left' ] )
	# l_lists[ 0 ][ 'curses_win' ].clear()
	# l_lists[ 0 ][ 'curses_win' ].addstr( 'Hello World!' )
	# l_lists[ 0 ][ 'curses_win' ].border()

	#for item in l_lists : print( item )

	l_lists.append( ScrollList( p_stdscr, 'artists', True, 1, 0, int( l_available_screen_height * 0.75 ) - 3, int( l_available_screen_width / 3 ) - 1 ) )
	l_available_screen_width -= ( l_lists[ 0 ].m_left_int + l_lists[ 0 ].m_width_int + 1 )
	l_lists.append( ScrollList( p_stdscr, 'albums' , True, 1, l_lists[ 0 ].m_left_int + l_lists[ 0 ].m_width_int + 1, int( l_available_screen_height * 0.75 ) - 3, int( l_available_screen_width / 2 ) - 1 ) )
	l_available_screen_width -= ( l_lists[ 1 ].m_width_int + 1 )
	l_lists.append( ScrollList( p_stdscr, 'songs'  , True, 1, l_lists[ 1 ].m_left_int + l_lists[ 1 ].m_width_int + 1, int( l_available_screen_height * 0.75 ) - 3, l_available_screen_width - 1 ) )
	l_available_screen_height -= ( l_lists[ 0 ].m_height_int + 1 + 3 )
	l_lists.append( ScrollList( p_stdscr, 'log'    , False, l_lists[ 0 ].m_top_int + l_lists[ 0 ].m_height_int + 1 + 3, 0, l_available_screen_height, curses.COLS -1 ) )

	l_lists[ 0 ].m_curses_win_obj.addstr( 1, 1, 'Artists list' )
	l_lists[ 1 ].m_curses_win_obj.addstr( 1, 1, 'Albums list' )
	l_lists[ 2 ].m_curses_win_obj.addstr( 1, 1, 'Songs list' )
	l_lists[ 3 ].m_curses_win_obj.addstr( 1, 1, 'Logs list' )

	l_lists[ 0 ].redraw_list()
	l_lists[ 1 ].redraw_list()
	l_lists[ 2 ].redraw_list()
	l_lists[ 3 ].redraw_list()

	db_file_name_str = 'music.sqlite'
	# Init database and create tables, if new
	init_db( db_file_name_str )
	# Populate UI lists with data from database
	query_result = sqlite_get( db_file_name_str, 'SELECT * FROM artists' )
	for row in query_result[ 2 ] :
		l_lists[ 0 ].m_items_list.append( row )
	query_result = sqlite_get( db_file_name_str, 'SELECT * FROM albums' )
	for row in query_result[ 2 ] :
		l_lists[ 1 ].m_items_list.append( row )
	query_result = sqlite_get( db_file_name_str, 'SELECT * FROM songs' )
	for row in query_result[ 2 ] :
		l_lists[ 2 ].m_items_list.append( row )

	# Create menus
	l_quit_menu_choices =\
	{
		'choices' :
		[
			'No',
			'Yes'
		],
		'title' : 'Really quit?'
	}
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

	app_quit_flag = False
	while not app_quit_flag :
		p_stdscr.clear()
		_redraw_main_screen( p_stdscr, l_lists )
		#p_stdscr.refresh()
		l_input_key = p_stdscr.getch()
		p_stdscr.addstr( 2, 0, str( l_input_key ) )
		global _selected_list
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

	# Restore blinking cursor
	curses.curs_set( 1 )
