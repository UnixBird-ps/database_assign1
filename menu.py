import curses
from curses.textpad import rectangle
import curses.ascii
from utils import debug_info


def get_menu_choice( p_stdscr, p_choices_list, p_options = None ) :
	l_selected_int = 0
	l_shown_cols_list = [ 1 ] #range( len( p_choices_list[ 'choices' ][ 0 ] ) )
	l_justify_list = [ 'center' ] * len( p_choices_list[ 'choices' ][ 0 ] )
	if not p_options is None :
		if 'selected_int' in list( p_options ) : l_selected_int = p_options.get( 'selected_int' )
		if 'shown_cols_list' in list( p_options ) : l_shown_cols_list = p_options.get( 'shown_cols_list' )
		if 'justify_list' in list( p_options ) : l_justify_list = p_options.get( 'justify_list' )
	# Get the size of the screen
	l_scr_size_yx = p_stdscr.getmaxyx()
	# Calculate half width and height
	l_scr_ctr_yx = ( int( l_scr_size_yx[ 0 ] / 2 ), int( l_scr_size_yx[ 1 ] / 2 ) )
	# Set index of first visible item
	l_scroll_region_top_int = 0
	# Max lines in scrollable region if list does not fit on screen
	# Screen lines minus top bar, minus 2 dialog horizontal borders, minus title, minus one line gap, minus status bar
	l_max_visible_list_lines = min( l_scr_size_yx[ 0 ] - 1 - 2 - 2 - 1, len( p_choices_list[ 'choices' ] ) )
	# Find max num of cols
	l_num_of_fields = 0
	for choice_row in p_choices_list[ 'choices' ] :
		debug_info( f'length of choice_row:{ len( choice_row ) }  { choice_row }' )
		l_num_of_fields = max( l_num_of_fields, len( choice_row ) )
	debug_info( f'l_num_of_fields:{ l_num_of_fields }' )
	# Build a list of column widths
	# Start with 0 width
	l_widest_row_int = len( p_choices_list[ 'title' ] )
	# Set initial width of every column to 0
	l_col_width_list = [ 0 ] * l_num_of_fields #len( p_choices_list[ 'choices' ][ 0 ] )
	# Go through all rows
	for choice_itr, choice_row in enumerate( p_choices_list[ 'choices' ] ) :
		#debug_info( f'{ choice_itr }, { choice_row }' )
		# Go through all fields in a row to find widest common column width
		for field_itr, field_val in enumerate( choice_row ) :
			#debug_info( f'{ field_itr }, { field_val }' )
			#if field_idx not in l_shown_cols_list : break
			l_col_width_list[ field_itr ] = max( l_col_width_list[ field_itr ], len( str( field_val ) ) )
		l_widest_row_int = max( l_widest_row_int, sum( l_col_width_list ) )

	# Start with an empty list for multi-column rows
	l_concatenated_fields_list = []

	# Loop through all choice items, concatenate multiple fields in a row , find widest string
	for choice_idx, choice_row in enumerate( p_choices_list[ 'choices' ] ) :
		choice_itm_str = ''
		if len( list( choice_row ) ) > 1 :
			# Row contains multiple fields, concatenate them together
			for shown_col_itr, shown_col_value in enumerate( l_shown_cols_list ) :
				if shown_col_itr > 0 :
					choice_itm_str += '  '
				if 0 <= shown_col_value < len( choice_row ) :
					# Store the value
					field_value = choice_row[ list( choice_row )[ shown_col_value ] ]
					l_justify_value = l_justify_list[ shown_col_itr ]
					match l_justify_value :
						case 'left' :
							choice_itm_str += str( field_value ).ljust( l_col_width_list[ shown_col_value ] )
						case 'right' :
							choice_itm_str += str( field_value ).rjust( l_col_width_list[ shown_col_value ] )
						case 'center' :
							choice_itm_str += str( field_value ).center( l_col_width_list[ shown_col_value ] )
			# Adjust widest width
			l_widest_row_int = max( l_widest_row_int, len( choice_itm_str ) )
		elif len( choice_row ) == 1 :
			choice_itm_str += str( choice_row[ 0 ] )

		# Add padding
		l_padded_row_str = '<' + f'>{ choice_itm_str }<'.center( l_widest_row_int ) + '>'
		# Add row to list
		l_concatenated_fields_list.append( l_padded_row_str )

	# Size of the dialog
	l_dlg_size_yx =\
	(
		# vertical:   top border + title + gap + number of choices + bottom border
		min( l_scr_size_yx[ 0 ] - 2, l_max_visible_list_lines + 1 + 1 + 1 ),
		# horizontal: left border + padded widest string + right border
		min( l_scr_size_yx[ 1 ], 1 + l_widest_row_int + 1 + 1 )
	)

	# Calculate half menu width and height
	l_menu_half_yx = ( int( l_dlg_size_yx[ 0 ] / 2 ), int( l_dlg_size_yx[ 1 ] / 2 ) )

	# Calculate upper left corner coords
	l_ulyx =\
	(
		max( 1, l_scr_ctr_yx[ 0 ] - l_menu_half_yx[ 0 ] - 1 ),
		max( 0, l_scr_ctr_yx[ 1 ] - l_menu_half_yx[ 1 ] )
	)
	# Calculate lower right corner coords
	l_lryx =\
	(
		min( p_stdscr.getmaxyx()[ 0 ], l_ulyx[ 0 ] + l_dlg_size_yx[ 0 ] ),
		min( p_stdscr.getmaxyx()[ 1 ] - 2, l_ulyx[ 1 ] + l_dlg_size_yx[ 1 ] )
	)

	rectangle( p_stdscr, l_ulyx[ 0 ], l_ulyx[ 1 ], l_lryx[ 0 ], l_lryx[ 1 ] )
	p_stdscr.refresh()

	l_newwin = p_stdscr.subwin(
		max( 1, l_dlg_size_yx[ 0 ] ),
		max( 1, l_dlg_size_yx[ 1 ] - 1 ),
		max( 1, l_ulyx[ 0 ] + 1 ),
		max( 0, l_ulyx[ 1 ] + 1 )
	)
	l_newwin.refresh()

	# Write the title
	l_newwin.addstr( 0, 0, p_choices_list[ 'title' ].center( l_widest_row_int + 2 ) )
	l_newwin.addstr( 1, 0, ''.center( l_widest_row_int + 2 ) )

	# Stay in menu loop until user hits ENTER or ESC key
	l_user_key = -1
	while l_user_key not in [ curses.KEY_ENTER, 459, 13, 10, 27 ] :
		# Lmits
		# Make sure the selector is within bounderies of the list
		if l_selected_int > len( p_choices_list[ 'choices' ] ) - 1 :
			l_selected_int = len( p_choices_list[ 'choices' ] ) - 1
		if l_selected_int < 0 : l_selected_int = 0
		# Make sure that the selector does not go beyond list's last visible item
		if l_scroll_region_top_int < l_selected_int - l_max_visible_list_lines + 1:
			l_scroll_region_top_int = l_selected_int - l_max_visible_list_lines + 1
		# Make sure that the selector does not go beyond list's first visible item
		if l_scroll_region_top_int > l_selected_int :
			l_scroll_region_top_int = l_selected_int
		# Make sure that the selector does not go beyond list's first index ( 0 )
		if l_scroll_region_top_int < 0 :
			l_scroll_region_top_int = 0

		# Display the menu choices
		for vis_idx in range( l_max_visible_list_lines ) : #enumerate( p_choices_list[ 'choices' ] ):
			# Calculate list index
			choice_idx = l_scroll_region_top_int + vis_idx
			# Make sure selected index is within bounds
			if choice_idx < 0 : break
			if choice_idx >= len( p_choices_list[ 'choices' ] ) : break

			#choice_row = p_choices_list[ 'choices' ][ choice_idx ]

			# Write row, with reversed colors if current row is selected
			if choice_idx == l_selected_int:
				l_newwin.addstr( 2 + vis_idx, 0, l_concatenated_fields_list[ choice_idx ], curses.A_REVERSE )
			else:
				l_newwin.addstr( 2 + vis_idx, 0, l_concatenated_fields_list[ choice_idx ] )
		# Get key from user
		l_user_key = l_newwin.getch()
		# Change selected item depending on user input
		match l_user_key :
			case curses.KEY_UP   : l_selected_int -= 1
			case curses.KEY_DOWN : l_selected_int += 1
			case 27 :
				l_selected_int = -1
				break
	# Destroy the window dialog
	del l_newwin
	# Return choice id to caller
	return l_selected_int


def get_string_from_input( p_stdscr, p_msg_str, p_input_length_max_int = 1 ) :
	# Get the size of the screen
	l_scr_size_yx = p_stdscr.getmaxyx()
	l_scr_ctr_yx = ( int( l_scr_size_yx[ 0 ] / 2 ), int( l_scr_size_yx[ 1 ] / 2 ) )
	# Set limit of input string length
	p_input_length_max_int = min( p_input_length_max_int, l_scr_size_yx[ 1 ] )
	# Calculate half screen width and half screen height
	l_dlg_half_size_yx = ( max( 1, int( 3 / 2 ) ), int( ( 1 + len( p_msg_str ) + p_input_length_max_int + 1 ) / 2 ) )
	# Calculate border coords
	l_dlg_ulyx = ( max( 1, l_scr_ctr_yx[ 0 ] - l_dlg_half_size_yx[ 0 ] ), max( 1, l_scr_ctr_yx[ 1 ] - l_dlg_half_size_yx[ 1 ] ) )
	l_dlg_lryx = (
		min( l_scr_size_yx[ 0 ], l_scr_ctr_yx[ 0 ] + l_dlg_half_size_yx[ 0 ] ),
		min( l_scr_size_yx[ 1 ], l_scr_ctr_yx[ 1 ] + l_dlg_half_size_yx[ 1 ] )
	)

	# Draw a rectangle around the dialog window
	rectangle( p_stdscr, l_dlg_ulyx[ 0 ], l_dlg_ulyx[ 1 ], l_dlg_lryx[ 0 ], l_dlg_lryx[ 1 ] )
	p_stdscr.refresh()

	# Create a new window inside the dialog rectangle
	l_newwin = p_stdscr.subwin( l_dlg_lryx[ 0 ] - l_dlg_ulyx[ 0 ] , l_dlg_lryx[ 1 ] - l_dlg_ulyx[ 1 ], l_dlg_ulyx[ 0 ] + 1, l_dlg_ulyx[ 1 ] + 1 )
	l_newwin.refresh()

	# Write the dialog message
	l_newwin.addstr( 0, 0, p_msg_str )

	# Restore blinking cursor
	curses.curs_set( 1 )
	l_user_key = -1
	l_input_str = ''
	# Stay in menu loop until user hits ENTER key
	while l_user_key not in [ curses.KEY_ENTER, 459, 13, 10, 27 ] :
		# Get key from user
		l_user_key = l_newwin.getch( 0, len( p_msg_str ) + len( l_input_str ) )
		match l_user_key :
			case curses.KEY_BACKSPACE | 8 :
				# Erase last sharacter in the input string
				if len( l_input_str ) > 0 :
					# Slice the string, remove last char
					l_input_str = l_input_str[:len( l_input_str )-1 ]
					# write a space behind the shortened string
					l_newwin.addstr( 0, len( p_msg_str ) + len( l_input_str ), ' ' )
			case _ :
				# Limit the length of input string
				if len( l_input_str ) < p_input_length_max_int :
					# Add only visible chars
					if curses.ascii.isalnum( l_user_key ) or curses.ascii.isprint( l_user_key ):
						l_char = chr( l_user_key )
						l_input_str += l_char
		# Write the string to the screen
		l_newwin.addstr( 0, len( p_msg_str ), l_input_str )
		l_newwin.refresh()
	# Destroy the window dialog
	del l_newwin
	# Hide blinking cursor
	curses.curs_set( 0 )
	# Return string to caller
	return l_input_str
