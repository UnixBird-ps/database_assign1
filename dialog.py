import curses
import curses.ascii
from curses.textpad import rectangle
from utils import debug_info


def dialog( p_curses_window_obj, p_org_dlg_dict = None ) :
	if p_org_dlg_dict is None : return

	# To add or modify props of the dialog without modifying the original
	l_temp_dlg_dict = {}#dict( p_dlg_dict )
	l_temp_dlg_dict |= { 'controls' : [] }

	# Get the size of the screen
	l_scr_size_yx = p_curses_window_obj.getmaxyx()
	# Calculate half width and height
	l_scr_ctr_yx = ( int( l_scr_size_yx[ 0 ] / 2 ), int( l_scr_size_yx[ 1 ] / 2 ) )

	l_keys_dict =\
	{
		'cancel' : { 'key_code' : 27,            'value' : False, 'key_desc' : 'ESC', 'cmd' : 'Cancel' },
		'save'   : { 'key_code' : curses.KEY_F2, 'value' : True,  'key_desc' : 'F2',  'cmd' : 'Save' }
	}

	# Write text at the bottom of screen the key/command pairs
	l_status_bar_text = ''
	for itr, key_attr_dict in enumerate( l_keys_dict.values() ) :
		if itr > 0 :
			l_status_bar_text += '   '
		#l_status_bar_text += f'{ key_in_dlg_dict.get( list( key_in_dlg_dict )[ 0 ] ) }:{ key_in_dlg_dict.get( list( key_in_dlg_dict )[ 0 ] ) }'
		l_status_bar_text += f'{ key_attr_dict.get( "key_desc" ) }:{ key_attr_dict.get( "cmd" ) }'
	# Make it centered, but cut last character to prevent an exception
	l_status_bar_text = l_status_bar_text.center( l_scr_size_yx[ 1 ] - 1 )
	# Output the bar on first row of the screen
	p_curses_window_obj.addnstr( l_scr_size_yx[ 0 ] - 1, 0, l_status_bar_text, l_scr_size_yx[ 1 ], curses.A_REVERSE )

	l_dlg_size_yx = p_org_dlg_dict.get( 'sizeyx' )
	l_dlg_inner_size_yx = ( l_dlg_size_yx[ 0 ] - 1, l_dlg_size_yx[ 1 ] - 1 )

	# Calculate half screen width and half screen height
	l_dlg_half_size_yx = ( int( p_org_dlg_dict.get( 'sizeyx' )[ 0 ] / 2 ), int( p_org_dlg_dict.get( 'sizeyx' )[ 1 ] / 2 ) )

	# Calculate coords for the dialog window
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
	l_dlg_wnd.bkgdset( ' ', curses.color_pair( 10 ) )
	l_dlg_wnd.clear()

	# Build a list of controls with properties
	l_ctl_height_aggr = 2 # Start placing controls at second line from the top of the dialog window
	for org_ctl_dict in p_org_dlg_dict.get( 'controls' ) :
		# Create a temp control dict
		l_new_ctl_dict = {}
		# Append new attribute to the new dict
		l_new_ctl_dict |= { 'label' : org_ctl_dict.get( 'label' ) }
		l_new_ctl_dict |= { 'max_length' : org_ctl_dict.get( 'max_length' ) }
		l_new_ctl_dict |= { 'value' : org_ctl_dict.get( 'value' ) }
		l_new_ctl_dict |= { 'pos_yx' : ( l_ctl_height_aggr, len( org_ctl_dict.get( 'label' ) ) + 1 ) }
		l_new_ctl_dict |= { 'caret_pos' : 0 }
		l_new_ctl_dict |= { 'cursor_yx' : [ 0, 0 ] }

		# Create rect coords for the text box where top left corner is positioned directly to the right of the label
		l_temp_ctl_rect =\
		{
			'h' : org_ctl_dict.get( 'lines' ),
			'w' : l_dlg_inner_size_yx[ 1 ] - 1 - l_new_ctl_dict.get( 'pos_yx' )[ 1 ],
			't' : l_new_ctl_dict.get( 'pos_yx' )[ 0 ],# + l_dlg_ulyx[ 0 ] + 1,
			'l' : l_new_ctl_dict.get( 'pos_yx' )[ 1 ],# + l_dlg_ulyx[ 1 ] + 1,
		}
		# Add the rect to the control's dict
		l_new_ctl_dict |= { 'rect' : l_temp_ctl_rect }
		# Add to total height of all controls added together
		l_ctl_height_aggr += org_ctl_dict.get( 'lines' ) + 1
		# Add the control's dict to the list of controls
		l_temp_dlg_dict[ 'controls' ].append( l_new_ctl_dict )

	# Create an empty list for text box windows
	l_ctl_wnds_list = []

	# Display the dialog title centered on first line
	l_dlg_wnd.addnstr( 0, 0 , p_org_dlg_dict.get( 'title' ).center( l_dlg_inner_size_yx[ 1 ] ), l_dlg_inner_size_yx[ 1 ] )

	# Display labels and values
	for ctl_dict in l_temp_dlg_dict.get( 'controls' ) :
		# Put the label 1 col from the left edge of the window
		l_dlg_wnd.addnstr( ctl_dict.get( 'pos_yx' )[ 0 ], 1, ctl_dict.get( 'label' ), len( ctl_dict.get( 'label' ) ) )

		# Create a window for the text box
		l_new_wnd = l_dlg_wnd.derwin( ctl_dict.get( 'rect' )[ 'h' ], ctl_dict.get( 'rect' )[ 'w' ], ctl_dict.get( 'rect' )[ 't' ], ctl_dict.get( 'rect' )[ 'l' ] )
		l_new_wnd.bkgdset( ' ', curses.color_pair( 0 ) )
		l_new_wnd.clear()

		# Write the value inside the textbox window
		l_new_wnd.addnstr( 0, 0, str( ctl_dict.get( 'value' ) ), ctl_dict.get( 'max_length' ), curses.color_pair( 1 ) )
		l_new_wnd.refresh()
		l_ctl_wnds_list.append( l_new_wnd )

	l_dlg_wnd.refresh()

	# Restore blinking cursor
	curses.curs_set( 1 )

	l_current_ctl_idx = 0

	l_return_value = False
	l_user_key = -1
	while l_user_key not in [ curses.KEY_F10, l_keys_dict.get( 'cancel' ).get( 'key_code' ), l_keys_dict.get( 'save' ).get( 'key_code' ) ] : #, curses.KEY_ENTER, 459, 13, 10
		# Get attributes for later use
		l_current_ctl_dict = l_temp_dlg_dict.get( 'controls' )[ l_current_ctl_idx ]
		l_current_ctl_wnd = l_ctl_wnds_list[ l_current_ctl_idx ]

		# Write the value to window
		l_current_ctl_wnd.addnstr( 0, 0, str( l_current_ctl_dict.get( 'value' ) ) + ' ', 1 + l_current_ctl_dict.get( 'max_length' ), curses.color_pair( 0 ) )

		# Move cursor to the control that has focus
		l_current_ctl_dict.get( "cursor_yx" )[ 0 ] = int( l_current_ctl_dict[ 'caret_pos' ] / l_current_ctl_dict[ 'rect' ][ 'w' ] )
		l_current_ctl_dict.get( "cursor_yx" )[ 1 ] = int( l_current_ctl_dict[ 'caret_pos' ] % l_current_ctl_dict[ 'rect' ][ 'w' ] )
		l_current_ctl_wnd.move( l_current_ctl_dict.get( "cursor_yx" )[ 0 ], l_current_ctl_dict.get( "cursor_yx" )[ 1 ] )

		# Get key from user
		l_user_key = l_current_ctl_wnd.getch()

		# Split the whole string where the caret position is
		l_value_left_part  = l_current_ctl_dict[ 'value' ][ :l_current_ctl_dict[ 'caret_pos' ] ]
		l_value_right_part = l_current_ctl_dict[ 'value' ][ l_current_ctl_dict[ 'caret_pos' ]: ]
		match l_user_key :
			case curses.KEY_F2 :
				l_return_value = True
			case 9 :   # Missing curses.KEY_TAB
				l_current_ctl_idx += 1
				if l_current_ctl_idx >= len( l_temp_dlg_dict.get( 'controls' ) ) : l_current_ctl_idx = 0
			case 351 : # Missing curses.KEY_TAB + SHIFT
				l_current_ctl_idx -= 1
				if l_current_ctl_idx < 0 : l_current_ctl_idx = len( l_temp_dlg_dict.get( 'controls' ) ) - 1
				if l_current_ctl_idx < 0 : l_current_ctl_idx = 0
			case curses.KEY_LEFT :
				if l_current_ctl_dict[ 'caret_pos' ] > 0 : l_current_ctl_dict[ 'caret_pos' ] -= 1
			case curses.KEY_RIGHT :
				if l_current_ctl_dict[ 'caret_pos' ] < len( l_current_ctl_dict[ 'value' ] ) : l_current_ctl_dict[ 'caret_pos' ] += 1
			case curses.KEY_UP :
				# Move caret position in the string right a full width of the window, moving it up one line
				if l_current_ctl_dict[ 'caret_pos' ] >= l_current_ctl_dict[ 'rect' ][ 'w' ] :
					l_current_ctl_dict[ 'caret_pos' ] -= l_current_ctl_dict[ 'rect' ][ 'w' ]
			case curses.KEY_DOWN :
				# Move down only if the caret position is not on the last line
				if int( l_current_ctl_dict[ 'caret_pos' ] / l_current_ctl_dict[ 'rect' ][ 'w' ] ) < int( len( l_current_ctl_dict[ 'value' ] ) / l_current_ctl_dict[ 'rect' ][ 'w' ] ) :
					# Move caret position in the string left a full width of the window, moving it down one line
					l_current_ctl_dict[ 'caret_pos' ] += l_current_ctl_dict[ 'rect' ][ 'w' ]
					# If the caret position ends up beyond the length of the string, move it to the end of the string
					if l_current_ctl_dict[ 'caret_pos' ] > len( l_current_ctl_dict[ 'value' ] ) :
						l_current_ctl_dict[ 'caret_pos' ] = len( l_current_ctl_dict[ 'value' ] )
			case curses.KEY_HOME :
				l_current_ctl_dict[ 'caret_pos' ] = 0
			case curses.KEY_END :
				l_current_ctl_dict[ 'caret_pos' ] = len( l_current_ctl_dict[ 'value' ] )
			case curses.KEY_BACKSPACE | 8 :
				# Erase last sharacter in the input string
				if len( l_current_ctl_dict[ 'value' ] ) > 0 :
					# Slice the string, remove last char
					if len( l_value_left_part ) > 0 :
						l_current_ctl_dict[ 'value' ] = l_value_left_part[ :-1 ] + l_value_right_part
						l_current_ctl_dict[ 'caret_pos' ] -= 1
			case curses.KEY_DC : # curses.KEY_DELETE
				if len( l_value_right_part ) > 0 :
					l_current_ctl_dict[ 'value' ] = l_value_left_part + l_value_right_part[ 1: ]
			case _ :
				# Limit the length of input string
				if len( l_current_ctl_dict[ 'value' ] ) < l_current_ctl_dict.get( 'max_length' ) :
					# Add only visible chars
					if curses.ascii.isalnum( l_user_key ) or curses.ascii.isprint( l_user_key ) :
						l_char = chr( l_user_key )
						l_current_ctl_dict[ 'value' ] = l_value_left_part + l_char + l_value_right_part
						l_current_ctl_dict[ 'caret_pos' ] += 1


	# Destroy the windows of the controls
	for o in reversed( l_ctl_wnds_list  ):
		if o is not None : del o

	# Destroy the dialog window
	if l_dlg_wnd is not None : del l_dlg_wnd

	# Hide blinking cursor
	curses.curs_set( 0 )

	l_changed_flag = False
	for ctl_itr, ctl in enumerate( l_temp_dlg_dict.get( 'controls' ) ) :
		if p_org_dlg_dict[ 'controls' ][ ctl_itr ][ 'value' ] != ctl[ 'value' ] :
			p_org_dlg_dict[ 'controls' ][ ctl_itr ][ 'value' ] = ctl[ 'value' ]
			l_changed_flag = True

	# Return a flag indicating that values should be saved
	return l_changed_flag, l_return_value


def get_value_from_ctl_dict_list( p_ctl_name, p_ctl_dict_list ) :
	# Iterate through the list of controls
	for ctl_dict in p_ctl_dict_list :
		if ctl_dict.get( 'name' ) == p_ctl_name :
			return ctl_dict.get( 'value' )
	# Not found
	return None
