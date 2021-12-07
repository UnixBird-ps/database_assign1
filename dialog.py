import curses
import curses.ascii
from curses.textpad import rectangle
from utils import debug_info


def dialog( p_curses_window_obj, p_dlg_desc = None ) :
	if p_dlg_desc is None : return

	p_dlg_desc.get( 'controls' )

	# Get the size of the screen
	l_scr_size_yx = p_curses_window_obj.getmaxyx()
	# Calculate half width and height
	l_scr_ctr_yx = ( int( l_scr_size_yx[ 0 ] / 2 ), int( l_scr_size_yx[ 1 ] / 2 ) )

	l_dlg_size_yx = p_dlg_desc.get( 'sizeyx' )
	l_dlg_inner_size_yx = ( l_dlg_size_yx[ 0 ] - 1, l_dlg_size_yx[ 1 ] - 1 )
	# top border + gap + height of all controls and gaps betweeen them + bottom border

	# Calculate half screen width and half screen height
	l_dlg_half_size_yx = ( int( p_dlg_desc.get( 'sizeyx' )[ 0 ] / 2 ), int( p_dlg_desc.get( 'sizeyx' )[ 1 ] / 2 ) )

	l_dlg_ulyx = ( max( 1, l_scr_ctr_yx[ 0 ] - l_dlg_half_size_yx[ 0 ] ), max( 1, l_scr_ctr_yx[ 1 ] - l_dlg_half_size_yx[ 1 ] ) )
	l_dlg_lryx = (
		min( l_scr_size_yx[ 0 ], l_dlg_ulyx[ 0 ] + l_dlg_size_yx[ 0 ] ),
		min( l_scr_size_yx[ 1 ], l_dlg_ulyx[ 1 ] + l_dlg_size_yx[ 1 ] )
	)

	# Draw a rectangle around the dialog window
	rectangle( p_curses_window_obj, l_dlg_ulyx[ 0 ], l_dlg_ulyx[ 1 ], l_dlg_lryx[ 0 ], l_dlg_lryx[ 1 ] )
	p_curses_window_obj.refresh()

	# Create a new window inside the dialog rectangle
	l_dlg_wnd = p_curses_window_obj.subwin( l_dlg_inner_size_yx[ 0 ], l_dlg_inner_size_yx[ 1 ], l_dlg_ulyx[ 0 ] + 1, l_dlg_ulyx[ 1 ] + 1 )
	#l_dlg_wnd = curses.newwin( l_dlg_inner_size_yx[ 0 ], l_dlg_inner_size_yx[ 1 ], l_dlg_ulyx[ 0 ] + 1, l_dlg_ulyx[ 1 ] + 1 )
	l_dlg_wnd.bkgdset( ' ', curses.color_pair( 10 ) )
	l_dlg_wnd.clear()

	l_ctl_height_aggr = 2 # Start placing controls at second line from the top of the dialog window
	for itr, ctl_dict in enumerate( p_dlg_desc.get( 'controls' ) ) :
		# Append new attribute to the dict x
		ctl_dict |= { 'pos_yx' : ( l_ctl_height_aggr, len( ctl_dict.get( 'label' ) ) + 1 ) }
		ctl_dict |= { 'caret_pos' : 0 }
		ctl_dict |= { 'cursor_yx' : [ 0, 0 ] }
		# Add to total height of all controls added together
		l_ctl_height_aggr += ctl_dict.get( 'lines' ) + 1

	l_ctl_wnds_list = []

	# Write the dialog title centered on first line
	l_dlg_wnd.addnstr( 0, 0 , p_dlg_desc.get( 'title' ).center( l_dlg_inner_size_yx[ 1 ] ), l_dlg_inner_size_yx[ 1 ] )
	# Write labels and values
	for ctl_dict in p_dlg_desc.get( 'controls' ) :
		# Put the label 1 col from the left edge of the window
		l_dlg_wnd.addnstr( ctl_dict.get( 'pos_yx' )[ 0 ], 1, ctl_dict.get( 'label' ), len( ctl_dict.get( 'label' ) ) )

		# Create a window where top left corner is positioned directly to the right of the label
		# Window( height, width, top, left )
		l_ctl_rect =\
		{
			'h' : ctl_dict.get( "lines" ),
			'w' : l_dlg_inner_size_yx[ 1 ] - 1 - ctl_dict.get( "pos_yx" )[ 1 ],
			't' : ctl_dict.get( "pos_yx" )[ 0 ],# + l_dlg_ulyx[ 0 ] + 1,
			'l' : ctl_dict.get( "pos_yx" )[ 1 ],# + l_dlg_ulyx[ 1 ] + 1,
		}

		ctl_dict |= { 'rect' : l_ctl_rect }

		l_new_wnd = l_dlg_wnd.derwin( l_ctl_rect[ 'h' ], l_ctl_rect[ 'w' ], l_ctl_rect[ 't' ], l_ctl_rect[ 'l' ] )
		l_new_wnd.bkgdset( ' ', curses.color_pair( 0 ) )
		l_new_wnd.clear()

		# Write the value inside the textbox window
		#l_new_wnd.addnstr( 0, 0, ctl_dict.get( 'value' ), l_dlg_inner_size_yx[ 1 ] - 2 - len( ctl_dict.get( 'label' ) ), curses.color_pair( 1 ) )
		l_new_wnd.addnstr( 0, 0, ctl_dict.get( 'value' ), ctl_dict.get( 'max_length' ), curses.color_pair( 1 ) )
		l_new_wnd.refresh()
		l_ctl_wnds_list.append( l_new_wnd )

	l_dlg_wnd.refresh()
	# Destroy the dialog window
	#if l_dlg_wnd is not None : del l_dlg_wnd

	# Restore blinking cursor
	curses.curs_set( 1 )

	l_current_ctl_idx = 0

	l_user_key = -1
	while l_user_key not in [ curses.KEY_ENTER, 459, 13, 10, 27 ] :
		# Get attributes for later use
		l_current_ctl_dict = p_dlg_desc.get( 'controls' )[ l_current_ctl_idx ]
		l_ctl_rect = p_dlg_desc.get( 'rect' )
		l_current_ctl_wnd = l_ctl_wnds_list[ l_current_ctl_idx ]

		#l_current_ctl_wnd.addnstr( 0, 0, l_current_ctl_dict.get( 'value' ), l_current_ctl_dict.get( 'max_length' ), curses.color_pair( 0 ) )
		l_current_ctl_wnd.addnstr( 0, 0, l_current_ctl_dict.get( 'value' ) + ' ', 1 + l_current_ctl_dict.get( 'max_length' ), curses.color_pair( 0 ) )

		# Move cursor to the control that has focus
		# #l_ctl_wnd_pos_yx = l_ctl_dict.get( 'pos_yx' )
		# l_ctl_wnd_pos_yx = l_ctl_wnds_list[ l_current_ctl_idx ].getparyx()
		# l_ctl_wnd_pos_yx = l_current_ctl_wnd.getparyx()
		# l_dlg_wnd.move( l_ctl_wnd_pos_yx[ 0 ], l_ctl_wnd_pos_yx[ 1 ] )

		l_current_ctl_dict.get( "cursor_yx" )[ 0 ] = int( l_current_ctl_dict[ 'caret_pos' ] / l_current_ctl_dict[ 'rect' ][ 'w' ] )
		l_current_ctl_dict.get( "cursor_yx" )[ 1 ] = int( l_current_ctl_dict[ 'caret_pos' ] % l_current_ctl_dict[ 'rect' ][ 'w' ] )
		l_current_ctl_wnd.move( l_current_ctl_dict.get( "cursor_yx" )[ 0 ], l_current_ctl_dict.get( "cursor_yx" )[ 1 ] )

		# l_new_wnd = p_curses_window_obj.derwin( l_ctl_rect[ 'h' ], l_ctl_rect[ 'w' ], l_ctl_rect[ 't' ], l_ctl_rect[ 'l' ] )
		# l_new_wnd.addnstr( 0, 0, l_current_ctl_dict.get( 'value' ), l_current_ctl_dict.get( 'max_length' ), curses.color_pair( 1 ) )
		# l_new_wnd.refresh()

		# Get key from user
		#l_user_key = l_dlg_wnd.getch( l_ctl_wnd_pos_yx[ 0 ], l_ctl_wnd_pos_yx[ 1 ] + len( l_current_ctl_dict[ 'value' ] ) )
		#l_user_key = l_current_ctl_wnd.getch( 0, len( l_current_ctl_dict[ 'value' ] ) )
		#l_user_key = l_new_wnd.getch( 0, len( l_current_ctl_dict[ 'value' ] ) )
		l_user_key = l_current_ctl_wnd.getch()
		#p_curses_window_obj.addnstr( 0, 0, str( l_user_key ) + ' ', 40 )

		l_value_left_part = l_current_ctl_dict[ 'value' ][ :l_current_ctl_dict[ 'caret_pos' ] ]
		l_value_right_part = l_current_ctl_dict[ 'value' ][ l_current_ctl_dict[ 'caret_pos' ]: ]
		match l_user_key :
			case 9 :   # Missing curses.KEY_TAB
				l_current_ctl_idx += 1
				if l_current_ctl_idx >= len( p_dlg_desc.get( 'controls' ) ) : l_current_ctl_idx = 0
			case 351 : # Missing curses.KEY_TAB + SHIFT
				l_current_ctl_idx -= 1
				if l_current_ctl_idx < 0 : l_current_ctl_idx = len( p_dlg_desc.get( 'controls' ) ) - 1
				if l_current_ctl_idx < 0 : l_current_ctl_idx = 0
			case curses.KEY_LEFT :
				if l_current_ctl_dict[ 'caret_pos' ] > 0 : l_current_ctl_dict[ 'caret_pos' ] -= 1
			case curses.KEY_RIGHT :
				if l_current_ctl_dict[ 'caret_pos' ] < len( l_current_ctl_dict[ 'value' ] ) : l_current_ctl_dict[ 'caret_pos' ] += 1
			case curses.KEY_UP :
				if l_current_ctl_dict[ 'caret_pos' ] >= l_current_ctl_dict[ 'rect' ][ 'w' ] :
					l_current_ctl_dict[ 'caret_pos' ] -= l_current_ctl_dict[ 'rect' ][ 'w' ]
			case curses.KEY_DOWN :
				pass
			case curses.KEY_BACKSPACE | 8 :
				# Erase last sharacter in the input string
				if len( l_current_ctl_dict[ 'value' ] ) > 0 :
					# Slice the string, remove last char
					#l_input_str = l_input_str[ : len( l_input_str ) - 1 ]
					#l_current_ctl_dict[ 'value' ] = l_current_ctl_dict[ 'value' ][ : len( l_current_ctl_dict[ 'value' ] ) - 1 ]
					if len( l_value_left_part ) > 0 :
						l_current_ctl_dict[ 'value' ] = l_value_left_part[ :-1 ] + l_value_right_part
						l_current_ctl_dict[ 'caret_pos' ] -= 1
					# write a space behind the shortened string
					#l_current_ctl_wnd.addnstr( 0, 0, l_current_ctl_dict.get( 'value' ) + ' ', l_current_ctl_dict.get( 'max_length' ), curses.color_pair( 1 ) )
					#l_current_ctl_wnd.addnstr( 0, 0, l_current_ctl_dict.get( 'value' ) + ' ', l_current_ctl_dict.get( 'max_length' ), curses.color_pair( 0 ) )
					#l_current_ctl_dict[ 'cursor_yx' ] = [ l_current_ctl_wnd.getyx()[ 0 ], l_current_ctl_wnd.getyx()[ 1 ] ]
			case curses.KEY_DC : # curses.KEY_DELETE
				if len( l_value_right_part ) > 0 :
					l_current_ctl_dict[ 'value' ] = l_value_left_part + l_value_right_part[ 1: ]
			case _ :
				# Limit the length of input string
				if len( l_current_ctl_dict[ 'value' ] ) < l_current_ctl_dict.get( 'max_length' ) :
					# Add only visible chars
					if curses.ascii.isalnum( l_user_key ) or curses.ascii.isprint( l_user_key ) :
						l_char = chr( l_user_key )
						#l_input_str += l_char
						l_current_ctl_dict[ 'value' ] = l_value_left_part + l_char + l_value_right_part
						l_current_ctl_dict[ 'caret_pos' ] += 1
						#l_current_ctl_wnd.insch( l_char )
						#l_current_ctl_wnd.addnstr( 0, 0, l_current_ctl_dict.get( 'value' ), l_current_ctl_dict.get( 'max_length' ), curses.color_pair( 0 ) )
						#l_current_ctl_dict[ 'cursor_yx' ] = [ l_current_ctl_wnd.getyx()[ 0 ], l_current_ctl_wnd.getyx()[ 1 ] ]

		# Write the value string right of the label
		#l_dlg_wnd.addnstr( l_current_ctl_dict.get( 'pos_yx' )[ 0 ], l_current_ctl_dict.get( 'pos_yx' )[ 1 ], l_ctl_dict.get( 'value' ), l_dlg_inner_size_yx[ 1 ] - 2 - len( ctl_dict.get( 'label' ) ), curses.color_pair( 1 ) )
		#l_dlg_wnd.addnstr( l_current_ctl_dict.get( 'pos_yx' )[ 0 ], l_current_ctl_dict.get( 'pos_yx' )[ 1 ], l_ctl_dict.get( 'value' ), l_current_ctl_dict.get( 'max_length' ), curses.color_pair( 1 ) )
		#l_ctl_wnds_list[ l_current_ctl_idx ].addnstr( 0, 0, l_ctl_dict.get( 'value' ), l_current_ctl_dict.get( 'max_length' ), curses.color_pair( 1 ) )
		#l_ctl_wnds_list[ l_current_ctl_idx ].addnstr( 0, 0, l_ctl_dict.get( 'value' ) + ' ', l_current_ctl_dict.get( 'max_length' ), curses.color_pair( 1 ) )
		#l_current_ctl_wnd.addnstr( 0, 0, l_current_ctl_dict.get( 'value' ), l_current_ctl_dict.get( 'max_length' ), curses.color_pair( 1 ) )
		#l_current_ctl_wnd.addnstr( 0, 0, l_current_ctl_dict.get( 'value' ), l_current_ctl_dict.get( 'max_length' ), curses.color_pair( 0 ) )
		#l_current_ctl_wnd.move( l_current_ctl_dict.get( "cursor_yx" )[ 0 ], l_current_ctl_dict.get( "cursor_yx" )[ 1 ] )

		#l_current_ctl_dict[ 'cursor_yx' ] = [ l_current_ctl_wnd.getyx()[ 0 ], l_current_ctl_wnd.getyx()[ 1 ] ]

		#l_current_ctl_wnd.refresh()
		#l_dlg_wnd.refresh()

		#l_input_str = l_ctl_dict[ 'value' ]

		#if l_new_wnd is not None : del l_new_wnd

	# Destroy the windows of the controls
	for o in reversed( l_ctl_wnds_list  ):
		if o is not None : del o

	# Destroy the dialog window
	if l_dlg_wnd is not None : del l_dlg_wnd

	# Hide blinking cursor
	curses.curs_set( 0 )

	# Return dialog values to caller
	return p_dlg_desc
