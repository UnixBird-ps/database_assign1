import curses, time
from dbutil import sqlite_get
from setup import init_db
from menu import get_menu_choice, get_string_from_input

def main( p_stdscr ) :
	"""

	:type stdscr: _curses.window
	"""
	# db_file_name_str = 'music.sqlite'
	# Create tables
	# init_db( db_file_name_str )
	# query_result = sqlite_get( db_file_name_str, 'SELECT * FROM songs' )
	# for row_idx, row in enumerate( query_result[ 2 ] ) :
	# 	print( f"( '{ row[ 1 ] }', { row[ 2 ] }, { row[ 3 ] } )" + ( '', ',' )[ row_idx < len( query_result[ 2 ] ) - 1 ] )
	# user_input = str( input( 'Enter album name:' ) )
	# print( f'user_input:>{user_input}<' )

	# Hide blinking cursor
	curses.curs_set( 0 )
	# Clear the screen
	p_stdscr.scrollok( True )
	p_stdscr.idlok( 1 )
	#stdscr.clear()

	#stdscr.addstr( 0, 0, "Current mode: Typing mode", curses.A_REVERSE )
	#stdscr.refresh()

	l_top_menu_choices =\
	{
		'title' : 'Main menu',
		'choices' :\
		[
			'Search ...',
			'Add    ...',
			'Quit   ...'
		]
	}

	l_quit_menu_choices =\
	{
		'title' : 'Really quit?',
		'choices' :\
		[
			'No',
			'Yes'
		]
	}

	l_add_menu_choices =\
	{
		'title' : 'Add music. What to add?',
		'choices' :\
		[
			'Add artist ...',
			'Add album  ...',
			'Add song   ...',
			'Go back'
		]
	}

	app_quit_flag = False
	while not app_quit_flag :
		l_menu_choice = get_menu_choice( p_stdscr, l_top_menu_choices )
		match l_menu_choice :
			case 0 :
				# The search dialog
				p_stdscr.clear()
				l_user_input_str = get_string_from_input( p_stdscr, 'Enter search term' )
				p_stdscr.addstr( 0, 0, l_user_input_str )
				p_stdscr.refresh()
			case 1 :
				# The Add menu
				p_stdscr.clear()
				l_add_menu_choice = get_menu_choice( p_stdscr, l_add_menu_choices )
			case 2 :
				l_quit_menu_choice = get_menu_choice( p_stdscr, l_quit_menu_choices )
				match l_quit_menu_choice :
					case 0:
						pass
					case 1 : app_quit_flag = True

	# Restore blinking cursor
	curses.curs_set( 1 )


