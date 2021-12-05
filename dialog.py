

def dialog( p_curses_window_obj, p_name, p_disabled_keys = None ) :
	m_curses_win_obj = p_curses_window_obj
	m_name = p_name
	# Get the size of the screen
	l_scr_size_yx = p_curses_window_obj.getmaxyx()
	# Calculate half width and height
	l_scr_ctr_yx = ( int( l_scr_size_yx[ 0 ] / 2 ), int( l_scr_size_yx[ 1 ] / 2 ) )
