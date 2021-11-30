import curses
from curses.textpad import rectangle


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
	while l_user_key not in [ curses.KEY_ENTER, 10, 13 ]:
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


def get_string_from_input( p_stdscr, p_msg_str ) :
	# Restore blinking cursor
	curses.curs_set( 1 )
	# Turn echoing on
	curses.echo()
	p_stdscr.addstr( 1, 0, p_msg_str + ': ' )
	# Get string from user input
	l_input_str = str( p_stdscr.getstr( 60 ), encoding = 'utf-8' )
	# Turn echoing off
	curses.noecho()
	# Hide blinking cursor
	curses.curs_set( 0 )
	# Return string to caller
	return l_input_str
