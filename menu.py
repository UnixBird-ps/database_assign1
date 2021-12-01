import curses
from curses.textpad import rectangle
import curses.ascii

def get_menu_choice( p_stdscr, p_choice_strs_list, p_selected_int = 0 ) :
	# Clear the screen
	#p_stdscr.clear()
	# Get the size of the screen
	l_scr_size_yx = p_stdscr.getmaxyx()
	# Calculate half width and height
	l_center_yx = ( int( l_scr_size_yx[ 0 ] / 2 ), int( l_scr_size_yx[ 1 ] / 2 ) )
	# Find widest choice string
	l_widest_int = len( p_choice_strs_list[ 'title' ] )
	for itm_idx, itm_str in enumerate( p_choice_strs_list[ 'choices' ] ) :
		if len( itm_str ) > l_widest_int : l_widest_int = len( itm_str )
	# Calculate half menu width and height
	l_menu_half_yx = ( int( len( p_choice_strs_list ) / 2 ), int( l_widest_int / 2 ) )

	l_yx = ( l_center_yx[ 0 ] - l_menu_half_yx[ 0 ] - 2, l_center_yx[ 1 ] - l_menu_half_yx[ 1 ] )

	l_ulyx = ( max( 1, l_yx[ 0 ] - 1 ), max( 1, l_yx[ 1 ] - 1 ) )
	l_lryx = (
		min( p_stdscr.getmaxyx()[ 0 ], l_yx[ 0 ] + 2 + len( p_choice_strs_list[ 'choices' ] ) ),
		min( p_stdscr.getmaxyx()[ 1 ], l_yx[ 1 ] + 2 + l_widest_int )
	)

	l_newwin = p_stdscr.subwin(
		2 + len( p_choice_strs_list[ 'choices' ] ),
		2 + l_widest_int,
		max( 1, l_yx[ 0 ] - 1 ),
		max( 1, l_yx[ 1 ] - 1 )
	)
	l_newwin.clear()
	del l_newwin
	rectangle( p_stdscr, l_ulyx[ 0 ], l_ulyx[ 1 ], l_lryx[ 0 ], l_lryx[ 1 ] )

	# Write the title
	p_stdscr.addstr( l_yx[ 0 ], l_yx[ 1 ], p_choice_strs_list[ 'title' ].center( l_widest_int + 2 ) )

	# Stay in menu loop until user hits ENTER key
	l_user_key = -1
	while l_user_key not in [ curses.KEY_ENTER, 459, 13, 10 ] :
		# Make sure selected index is within boundery
		if p_selected_int > len( p_choice_strs_list[ 'choices' ] ) - 1: p_selected_int = len( p_choice_strs_list[ 'choices' ] ) - 1
		if p_selected_int < 0 : p_selected_int = 0
		# Display the menu
		for itm_idx, itm_str in enumerate( p_choice_strs_list[ 'choices' ] ):
			l_widen_str = itm_str.center( l_widest_int + 2 )
			l_yx = ( l_center_yx[ 0 ] - l_menu_half_yx[ 0 ] + itm_idx, l_center_yx[ 1 ] - l_menu_half_yx[ 1 ] )
			if itm_idx == p_selected_int:
				p_stdscr.addstr( l_yx[ 0 ], l_yx[ 1 ], l_widen_str, curses.A_REVERSE )
			else:
				p_stdscr.addstr( l_yx[ 0 ], l_yx[ 1 ], l_widen_str )
		# Get key from user
		l_user_key = p_stdscr.getch()
		# p_stdscr.addstr( 0, 0, str( l_user_key ) ) # For debugging: Tell the key code
		# Change selected item depending on user input
		match l_user_key :
			case curses.KEY_UP   : p_selected_int -= 1
			case curses.KEY_DOWN : p_selected_int += 1
			case 27 :
				p_selected_int = -1
				break
	# Return choice id to caller
	return p_selected_int


def get_string_from_input( p_stdscr, p_msg_str, p_max_length_int = 1 ) :
	# Get the size of the screen
	l_scr_size_yx = p_stdscr.getmaxyx()
	print( f'l_scr_size_yx:{l_scr_size_yx}' )
	l_scr_ctr_yx = ( int( l_scr_size_yx[ 0 ] / 2 ), int( l_scr_size_yx[ 1 ] / 2 ) )
	print( f'l_scr_ctr_yx:{l_scr_ctr_yx}' )
	# Set limit of input string length
	p_length_limit_int = min( p_max_length_int, l_scr_size_yx[ 1 ] )
	print( f'p_length_limit_int:{p_length_limit_int}' )
	# Calculate half screen width and half screen height
	l_dlg_half_size_yx = ( max( 2, int( 3 / 2 ) ), int( ( 1 + len( p_msg_str ) + p_length_limit_int + 1 ) / 2 ) )
	print( f'l_dlg_half_size_yx:{l_dlg_half_size_yx}' )
	# Calculate border coords
	l_ulyx = ( max( 1, l_scr_ctr_yx[ 0 ] - l_dlg_half_size_yx[ 0 ] ), max( 1, l_scr_ctr_yx[ 1 ] - l_dlg_half_size_yx[ 1 ] ) )
	l_lryx = (
		min( l_scr_size_yx[ 0 ], l_scr_ctr_yx[ 0 ] + l_dlg_half_size_yx[ 0 ] ),
		min( l_scr_size_yx[ 1 ], l_scr_ctr_yx[ 1 ] + l_dlg_half_size_yx[ 1 ] )
	)
	print( f'l_ulyx:{l_ulyx}' )
	print( f'l_lryx:{l_lryx}' )
	# Draw a rectangle around the dialog window
	rectangle( p_stdscr, l_ulyx[ 0 ], l_ulyx[ 1 ], l_lryx[ 0 ], l_lryx[ 1 ] )
	l_newwin = p_stdscr.subwin( l_lryx[ 0 ] - l_ulyx[ 0 ] , l_lryx[ 1 ] - l_ulyx[ 1 ], l_ulyx[ 0 ] + 1, l_ulyx[ 1 ] + 1 )
	l_newwin.box()

	l_newwin.addstr( 0, 0, p_msg_str )

	# Restore blinking cursor
	curses.curs_set( 1 )
	# Turn echoing on
	#curses.echo()
	l_user_key = -1
	l_input_str = ''
	# Stay in menu loop until user hits ENTER key
	while l_user_key not in [ curses.KEY_ENTER, 459, 13, 10, 27 ] :
		# Get key from user
		l_user_key = p_stdscr.getch()
		# CHECK: Tell the key code
		#p_stdscr.addstr( 0, 0, str( l_user_key ) )
		match l_user_key :
			case curses.KEY_BACKSPACE | 8 :
				l_input_str = l_input_str[:len( l_input_str ) ]
				l_newwin.addstr( 0, len( p_msg_str ) + len( l_input_str ), ' ' )
				# CHECK: Tell the key code
				#p_stdscr.addstr( 0, 0, 'KEY_BACKSPACE' )
			case _ :
				# Limit input string length
				if len( l_input_str ) < p_max_length_int :
					if curses.ascii.isalnum( l_user_key ) or curses.ascii.isprint( l_user_key ):
						l_char = chr( l_user_key )
						#l_newwin.addstr( l_scr_ctr_yx[ 0 ], l_scr_ctr_yx[ 1 ], l_char )
						l_input_str += l_char
						l_newwin.addnstr( 0, len( p_msg_str ), l_input_str, p_max_length_int )

	#l_input_str = str( l_newwin.getstr( 0, 0, p_max_length ), encoding = 'utf-8' )

	# Destroy the window dialog
	del l_newwin
	# Get string from user input
	#l_input_str = str( p_stdscr.getstr( p_max_length ), encoding = 'utf-8' )
	# Turn echoing off
	#curses.noecho()
	# Hide blinking cursor
	curses.curs_set( 0 )
	# Return string to caller
	return l_input_str
