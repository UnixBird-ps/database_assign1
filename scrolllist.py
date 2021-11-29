import curses
from curses.textpad import rectangle


class ScrollList :
	def __init__( self, p_parent_window_obj, p_name_str, p_editable_bool, p_lines_int, p_cols_int, p_top_int, p_left_int, p_disabled_keys = None ) :
		if p_disabled_keys is None : p_disabled_keys = []
		self.m_name_str = p_name_str
		self.m_editable_bool = p_editable_bool
		self.m_items_list = []
		self.m_selected_item_int = -1
		self.m_scroll_region_top_int = 0
		self.m_scroll_pointer_int = 0
		self.m_top_int = p_top_int
		self.m_left_int = p_left_int
		if p_lines_int < 3 : p_lines_int = 2
		if p_cols_int < 3 : p_cols_int = 2
		self.m_lines_int = p_lines_int
		self.m_cols_int = p_cols_int
		self.m_inner_lines_int = p_lines_int - 1
		self.m_inner_cols_int = p_cols_int - 1
		self.m_curses_win_parent_obj = None
		self.m_curses_win_obj = None
		self.m_disabled_keys = p_disabled_keys

		_curses_COLOR_WHITE = 8
		_curses_COLOR_LIGHTGRAY = 9
		_curses_COLOR_DARKGRAY = 10
		_curses_COLOR_YELLOW = 11
		curses.init_color( _curses_COLOR_WHITE, int(1000*255/255), int(1000*255/255), int(1000*255/255) )
		curses.init_color( _curses_COLOR_LIGHTGRAY, int(1000*191/255), int(1000*191/255), int(1000*191/255) )
		curses.init_color( _curses_COLOR_DARKGRAY, int(1000*127/255), int(1000*127/255), int(1000*127/255) )
		curses.init_color( _curses_COLOR_YELLOW, int(1000*255/255), int(1000*255/255), int(1000*0/255) )
		curses.init_pair( 1, _curses_COLOR_WHITE, curses.COLOR_BLACK )
		curses.init_pair( 2, _curses_COLOR_LIGHTGRAY, curses.COLOR_BLACK )
		curses.init_pair( 3, _curses_COLOR_DARKGRAY, curses.COLOR_BLACK )
		curses.init_pair( 4, _curses_COLOR_YELLOW, curses.COLOR_BLACK )
		curses.init_pair( 5, curses.COLOR_BLACK, _curses_COLOR_LIGHTGRAY )
		curses.init_pair( 6, curses.COLOR_BLACK, _curses_COLOR_DARKGRAY )
		self._WHITE_AND_BLACK = curses.color_pair( 1 )
		self._LIGHTGRAY_AND_BLACK = curses.color_pair( 2 )
		self._DARKGRAY_AND_BLACK = curses.color_pair( 3 )
		self._YELLOW_AND_BLACK = curses.color_pair( 4 )
		self._BLACK_AND_LIGHTGRAY = curses.color_pair( 5 )
		self._BLACK_AND_DARKGRAY = curses.color_pair( 6 )

		self.create_window( p_parent_window_obj )
		#self.m_curses_win_obj.scrollok( True )
		#self.m_curses_win_obj.idlok( 1 )


	def add_item( self, p_new_item_obj ) :
		self.m_items_list.append( p_new_item_obj )


	def create_window( self, p_parent ) :
		self.m_curses_win_parent_obj = p_parent
		self.m_curses_win_obj = p_parent.subwin( self.m_inner_lines_int + 1, self.m_inner_cols_int + 1, self.m_top_int + 1, self.m_left_int + 1 )


	def scroll_rel( self, p_rel_pos_int  ) :
		if len( self.m_items_list ) > 0 :
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


	def redraw_list( self, p_has_focus_bool, p_shown_cols = None ) :
		if p_shown_cols is None : p_shown_cols = []

		#self.m_curses_win_obj.border()

		if p_has_focus_bool : self.m_curses_win_parent_obj.attron( self._WHITE_AND_BLACK )
		else : self.m_curses_win_parent_obj.attron( self._DARKGRAY_AND_BLACK )
		rectangle(
			self.m_curses_win_parent_obj,
			self.m_top_int,
			self.m_left_int,
			self.m_top_int + self.m_lines_int,
			self.m_left_int + self.m_cols_int
		)
		if p_has_focus_bool : self.m_curses_win_parent_obj.attroff( self._WHITE_AND_BLACK )
		else : self.m_curses_win_parent_obj.attroff( self._DARKGRAY_AND_BLACK )

		# Put the name of the list on the border above the list
		self.m_curses_win_parent_obj.addnstr( self.m_top_int, self.m_left_int + 2, self.m_name_str.title(), self.m_inner_cols_int )

		if len( self.m_items_list ) > 0 :
			# find every col's width
			l_col_width_list = []
			for b_n in range( len( self.m_items_list[ 0 ] ) ): l_col_width_list.append( 0 )

			for i_row_idx, i_row in enumerate( self.m_items_list ):
				for i_col_idx, col in enumerate( i_row ) :
					l_width_int = len( str( col ) )
					if l_width_int > l_col_width_list[ i_col_idx ] :
						l_col_width_list[ i_col_idx ] = l_width_int

		for idx in range( self.m_inner_lines_int ) :
			# Calculate list index
			list_idx = self.m_scroll_region_top_int + idx
			# Make sure selected index is within boundery
			if list_idx < 0 : break
			if list_idx >= len( self.m_items_list ) : break

			# Get row elements
			itm = ''
			#for field_idx, field in enumerate( self.m_items_list[ list_idx ] ) :
			if len( p_shown_cols ) > 0 :
				for shown_idx_key, shown_idx_value in enumerate( p_shown_cols ) :
					l_value = self.m_items_list[ list_idx ][ shown_idx_value ]
					# Add space after first and following fields
					if shown_idx_key > 0 : itm += ' '
					# What columns in list to show
					itm += f'{ l_value }'
			else :
				# All if not specified
				for item_idx, item_value in self.m_items_list[ list_idx ] :
					if item_idx > 0 : itm += ' '
					itm += f'{ item_idx } { item_value }'

			# Add padding
			itm = itm[ : self.m_inner_cols_int - 2 ].ljust( self.m_inner_cols_int - 2 )

			# Mark selected item
			if list_idx == self.m_selected_item_int :
				itm = '>' + itm + '<'
			else :
				itm = ' ' + itm + ' '

			# Draw selection differently
			if list_idx == self.m_scroll_pointer_int and p_has_focus_bool :
				self.m_curses_win_obj.addnstr( 0 + idx, 0, itm, self.m_inner_cols_int, curses.A_REVERSE )
			elif list_idx == self.m_selected_item_int :
				self.m_curses_win_obj.addnstr( 0 + idx, 0, itm, self.m_inner_cols_int, self._BLACK_AND_DARKGRAY )
			else :
				self.m_curses_win_obj.addnstr( 0 + idx, 0, itm, self.m_inner_cols_int )

		#self.m_curses_win_parent_obj.addstr( self.m_top_int - 1, self.m_left_int + 1, str( self.m_scroll_pointer_int ) )

		self.m_curses_win_obj.refresh()


	def select_item_pointed( self ) :
		if len( self.m_items_list ) > 0 :
			self.m_selected_item_int = self.m_scroll_pointer_int
			return True
		else : return False


	def get_selected_item( self ) :
		if len( self.m_items_list ) > 0 :
			return self.m_items_list[ self.m_selected_item_int ]
		else : return None
