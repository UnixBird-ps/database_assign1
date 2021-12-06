import curses
from curses.textpad import rectangle
from utils import debug_info


def dialog( p_curses_window_obj, p_dlg_desc = None ) :
	if p_dlg_desc is None : return

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
	l_newwin = p_curses_window_obj.subwin( l_dlg_inner_size_yx[ 0 ], l_dlg_inner_size_yx[ 1 ], l_dlg_ulyx[ 0 ] + 1, l_dlg_ulyx[ 1 ] + 1 )

	l_newwin.bkgdset( ' ', curses.color_pair( 10 ) )
	l_newwin.clear()

	l_controls_list_size = len( p_dlg_desc.get( 'controls' ) )
	l_ctl_height_aggr = 2 # Start placing controls at second line from the top of the dialog window
	for itr, x in enumerate( p_dlg_desc.get( 'controls' ) ) :
		l_ctl_attr =	x.get( 'attr' )
		l_ctl_attr |= { 'pos_yx' : ( l_ctl_height_aggr, len( x.get( 'label' ) ) + 1 ) }
		l_ctl_height_aggr += l_ctl_attr.get( 'lines' ) + 1

	# Write the dialog title centered on first line
	l_newwin.addnstr( 0, 0 , p_dlg_desc.get( 'title' ).center( l_dlg_inner_size_yx[ 1 ] ), l_dlg_inner_size_yx[ 1 ] )

	for itr, x in enumerate( p_dlg_desc.get( 'controls' ) ) :
		l_newwin.addnstr( x.get( 'attr' ).get( 'pos_yx' )[ 0 ], 1, x.get( 'label' ), len( x.get( 'label' ) ) )
		l_newwin.addnstr( x.get( 'attr' ).get( 'pos_yx' )[ 0 ], x.get( 'attr' ).get( 'pos_yx' )[ 1 ], x.get( 'value' ), l_dlg_inner_size_yx[ 1 ] - 2 - len( x.get( 'label' ) ), curses.color_pair( 1 ) )
	l_newwin.refresh()

	# Restore blinking cursor
	curses.curs_set( 1 )

	l_current_ctl_idx = 0
	l_user_key = -1
	while l_user_key not in [ curses.KEY_ENTER, 459, 13, 10, 27 ] :
		# Move cursor to the control that has focus
		l_pos_yx = p_dlg_desc.get( 'controls' )[ l_current_ctl_idx ].get( 'attr' ).get( 'pos_yx' )
		l_newwin.move( l_pos_yx[ 0 ], l_pos_yx[ 1 ] )
		# Get key from user
		l_user_key = l_newwin.getch()# 0, len( p_msg_str ) + len( l_input_str ) )
		match l_user_key :
			case 9 :   # Missing curses.KEY_TAB
				l_current_ctl_idx += 1
				if l_current_ctl_idx >= l_controls_list_size : l_current_ctl_idx = 0
				# jump to control
			case 351 : # Missing curses.KEY_TAB + SHIFT
				l_current_ctl_idx -= 1
				if l_current_ctl_idx < 0 : l_current_ctl_idx = l_controls_list_size - 1
				if l_current_ctl_idx < 0 : l_current_ctl_idx = 0
				# jump to control


	# Destroy the window dialog
	del l_newwin
	# Hide blinking cursor
	curses.curs_set( 0 )
	# Return dialog values to caller
	return p_dlg_desc
