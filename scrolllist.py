import curses
from curses.textpad import rectangle


class ScrollList :
	def __init__( self, p_parent_window_obj, p_name_str, p_editable_bool, p_lines_int, p_cols_int, p_top_int, p_left_int ) :
		self.m_name_str = p_name_str
		self.m_editable_bool = p_editable_bool
		self.m_items_list = []
		self.m_selected_item_int = 0
		self.m_scroll_region_top_int = 0
		self.m_scroll_pointer_int = 0
		self.m_top_int = p_top_int
		self.m_left_int = p_left_int
		self.m_lines_int = p_lines_int
		self.m_cols_int = p_cols_int
		self.m_inner_lines_int = ( p_lines_int - 2, 1 )[ p_lines_int < 2 ]
		self.m_inner_cols_int = ( p_cols_int - 0, 1 )[ p_cols_int < 0 ]
		self.m_curses_win_parent_obj = None
		self.m_curses_win_obj = None

		self.create_window( p_parent_window_obj )
		#self.m_curses_win_obj.scrollok( True )
		#self.m_curses_win_obj.idlok( 1 )


	def add_item( self, p_new_item_obj ) :
		self.m_items_list.append( p_new_item_obj )


	def create_window( self, p_parent ) :
		self.m_curses_win_parent_obj = p_parent
		self.m_curses_win_obj = p_parent.subwin( self.m_lines_int, self.m_cols_int, self.m_top_int, self.m_left_int )


	def scroll_rel( self, p_rel_pos_int  ) :
		self.m_scroll_pointer_int += p_rel_pos_int

		if self.m_scroll_pointer_int > len( self.m_items_list ) - 1 :
			self.m_scroll_pointer_int = len( self.m_items_list ) - 1

		if self.m_scroll_pointer_int < 0 :
			self.m_scroll_pointer_int = 0

		if self.m_scroll_pointer_int < self.m_scroll_region_top_int :
			self.m_scroll_region_top_int = self.m_scroll_pointer_int

		if self.m_scroll_region_top_int < self.m_scroll_pointer_int - ( self.m_inner_lines_int - 1 ) :
			self.m_scroll_region_top_int = self.m_scroll_pointer_int - ( self.m_inner_lines_int - 1 )

		if self.m_scroll_region_top_int < 0 : self.m_scroll_region_top_int = 0

	def redraw_list( self, p_has_focus_bool ) :
		if p_has_focus_bool :
			self.m_curses_win_parent_obj.attron( curses.COLOR_WHITE )
			self.m_curses_win_obj.attron( curses.COLOR_WHITE )

		#self.m_curses_win_obj.border()

		l_y_int = self.m_top_int - 1
		l_x_int = self.m_left_int - 1
		rectangle(
			self.m_curses_win_parent_obj,
			l_y_int,
			l_x_int,
			l_y_int + self.m_lines_int + 1,
			l_x_int + self.m_cols_int + 1
		)

		self.m_curses_win_parent_obj.addnstr( self.m_top_int - 1, self.m_left_int + 1, self.m_name_str.title(), self.m_inner_cols_int )

		for idx in range( self.m_inner_lines_int ) :
			# Calculate list index
			list_idx = self.m_scroll_region_top_int + idx
			# Make sure selected index is within boundery
			if list_idx < 0 : break
			if list_idx >= len( self.m_items_list ) : break
			# Get list item
			itm = f'{ self.m_items_list[ list_idx ][ 0 ] } { self.m_items_list[ list_idx ][ 1 ][ 1 ] }'.ljust( self.m_inner_cols_int - 2 )

			if list_idx == self.m_selected_item_int :
				itm = '*' + itm + '*'
			else :
				itm = ' ' + itm + ' '

			if list_idx == self.m_scroll_pointer_int and p_has_focus_bool :
				self.m_curses_win_obj.addstr( 0 + idx, 0, itm, curses.A_REVERSE )
			else :
				self.m_curses_win_obj.addstr( 0 + idx, 0, itm )

		#self.m_curses_win_parent_obj.addstr( self.m_top_int - 1, self.m_left_int + 1, str( self.m_scroll_pointer_int ) )

		self.m_curses_win_obj.refresh()
