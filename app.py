import curses, time
from dbutil import sqlite_get
from setup import init_db


def main( stdscr ) :
	# Clear the screen
	stdscr.scrollok( True )
	stdscr.idlok( 1 )
	stdscr.clear()
	stdscr.refresh()
	#stdscr.nodelay( True )

	# db_file_name_str = 'music.sqlite'
	# Create tables
	# init_db( db_file_name_str )
	# query_result = sqlite_get( db_file_name_str, 'SELECT * FROM songs' )
	# for row_idx, row in enumerate( query_result[ 2 ] ) :
	# 	print( f"( '{ row[ 1 ] }', { row[ 2 ] }, { row[ 3 ] } )" + ( '', ',' )[ row_idx < len( query_result[ 2 ] ) - 1 ] )
	# user_input = str( input( 'Enter album name:' ) )
	# print( f'user_input:>{user_input}<' )

	app_quit_flag = False
	while not app_quit_flag :
		curses.echo()
		user_input = stdscr.getstr( 15 ).decode( 'utf-8' )
		stdscr.addstr( user_input + '\n' )
		curses.noecho()
		match user_input :
			case 'quit' | 'exit' : app_quit_flag = True # Exit the while loop
		stdscr.refresh()
