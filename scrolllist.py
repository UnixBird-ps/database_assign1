import curses
from curses.textpad import rectangle


class ScrollList :
	def __init__( self, p_parent_window_obj, p_name_str, p_editable_bool, p_lines_int, p_cols_int, p_top_int, p_left_int, p_auto_scroll_bool, p_disabled_keys = None ) :
		if p_disabled_keys is None : p_disabled_keys = []

		self.m_name_str = p_name_str

		# Get the size of the screen
		l_scr_size_yx = p_parent_window_obj.getmaxyx()

		p_top_int = max( 1, p_top_int )
		p_left_int = max( 0, p_left_int )
		self.m_top_int = p_top_int
		self.m_left_int = p_left_int
		p_lines_int = max( 3, p_lines_int )
		p_cols_int = max( 3, p_cols_int )
		p_lines_int = min( l_scr_size_yx[ 0 ] - p_top_int, p_lines_int )
		p_cols_int = min( l_scr_size_yx[ 1 ] - p_left_int, p_cols_int )
		self.m_lines_int = p_lines_int
		self.m_cols_int = p_cols_int
		self.m_inner_lines_int = p_lines_int - 1
		self.m_inner_cols_int = p_cols_int - 1
		self.m_items_list = []
		self.m_editable_bool = p_editable_bool
		self.m_selected_item_int = -1
		self.m_scroll_region_top_int = 0
		self.m_scroll_pointer_int = 0
		self.m_auto_scroll_bool = p_auto_scroll_bool
		self.m_disabled_keys = p_disabled_keys

		self.m_curses_win_parent_obj = None
		self.m_curses_win_obj = None

		_curses_COLOR_WHITE = 8
		_curses_COLOR_LIGHT_GRAY = 9
		_curses_COLOR_DARK_GRAY = 10
		_curses_COLOR_LIGHT_GREEN = 11
		_curses_COLOR_DARK_GREEN = 12
		_curses_COLOR_LIGHT_RED = 13
		_curses_COLOR_DARK_RED = 14
		_curses_COLOR_YELLOW = 15
		curses.init_color( _curses_COLOR_WHITE, int(1000*255/255), int(1000*255/255), int(1000*255/255) )
		curses.init_color( _curses_COLOR_LIGHT_GRAY, int(1000*191/255), int(1000*191/255), int(1000*191/255) )
		curses.init_color( _curses_COLOR_DARK_GRAY, int(1000*95/255), int(1000*95/255), int(1000*95/255) )
		curses.init_color( _curses_COLOR_LIGHT_GREEN, int(1000*0/255), int(1000*255/255), int(1000*0/255) )
		curses.init_color( _curses_COLOR_DARK_GREEN, int(1000*0/255), int(1000*127/255), int(1000*0/255) )
		curses.init_color( _curses_COLOR_LIGHT_RED, int(1000*255/255), int(1000*0/255), int(1000*0/255) )
		curses.init_color( _curses_COLOR_DARK_RED, int(1000*63/255), int(1000*0/255), int(1000*0/255) )
		curses.init_color( _curses_COLOR_YELLOW, int(1000*255/255), int(1000*255/255), int(1000*0/255) )
		curses.init_pair( 1, _curses_COLOR_WHITE, curses.COLOR_BLACK )
		curses.init_pair( 2, _curses_COLOR_LIGHT_GRAY, curses.COLOR_BLACK )
		curses.init_pair( 3, _curses_COLOR_DARK_GRAY, curses.COLOR_BLACK )
		curses.init_pair( 4, _curses_COLOR_LIGHT_GREEN, curses.COLOR_BLACK )
		curses.init_pair( 5, _curses_COLOR_DARK_GREEN, curses.COLOR_BLACK )
		curses.init_pair( 6, _curses_COLOR_LIGHT_RED, curses.COLOR_BLACK )
		curses.init_pair( 7, _curses_COLOR_DARK_RED, curses.COLOR_BLACK )
		curses.init_pair( 8, _curses_COLOR_YELLOW, curses.COLOR_BLACK )
		curses.init_pair( 9, curses.COLOR_BLACK, _curses_COLOR_LIGHT_GRAY )
		curses.init_pair( 10, curses.COLOR_BLACK, _curses_COLOR_DARK_GRAY )
		self._WHITE_AND_BLACK = curses.color_pair( 1 )
		self._LIGHT_GRAY_AND_BLACK = curses.color_pair( 2 )
		self._DARK_GRAY_AND_BLACK = curses.color_pair( 3 )
		self._LIGHT_GREEN_AND_BLACK = curses.color_pair( 4 )
		self._DARK_GREEN_AND_BLACK = curses.color_pair( 5 )
		self._LIGHT_RED_AND_BLACK = curses.color_pair( 6 )
		self._DARK_RED_AND_BLACK = curses.color_pair( 7 )
		self._YELLOW_AND_BLACK = curses.color_pair( 8 )
		self._BLACK_AND_LIGHT_GRAY = curses.color_pair( 9 )
		self._BLACK_AND_DARK_GRAY = curses.color_pair( 10 )

		self.create_window( p_parent_window_obj )
		#self.m_curses_win_obj.scrollok( True )
		#self.m_curses_win_obj.idlok( 1 )


	def create_window( self, p_parent ) :
		self.m_curses_win_parent_obj = p_parent
		self.m_curses_win_obj = p_parent.subwin( self.m_inner_lines_int + 1, self.m_inner_cols_int + 1, self.m_top_int + 1, self.m_left_int + 1 )


	def redraw_list( self, p_has_focus_bool, p_shown_cols = None ) :
		if p_shown_cols is None : p_shown_cols = []

		# Draw a border with a color depending on if this list has focus os not
		if p_has_focus_bool : self.m_curses_win_parent_obj.attron( self._LIGHT_GREEN_AND_BLACK )
		else : self.m_curses_win_parent_obj.attron( self._DARK_GRAY_AND_BLACK )
		rectangle(
			self.m_curses_win_parent_obj,
			self.m_top_int,
			self.m_left_int,
			self.m_top_int + self.m_lines_int,
			self.m_left_int + self.m_cols_int
		)
		if p_has_focus_bool : self.m_curses_win_parent_obj.attroff( self._LIGHT_GREEN_AND_BLACK )
		else : self.m_curses_win_parent_obj.attroff( self._DARK_GRAY_AND_BLACK )

		# Put the name of the list on the border above the list
		if p_has_focus_bool :
			self.m_curses_win_parent_obj.addnstr( self.m_top_int, self.m_left_int + 1, f' { self.m_name_str.title() } ', self.m_inner_cols_int - 3, self._LIGHT_GREEN_AND_BLACK )
		else :
			self.m_curses_win_parent_obj.addnstr( self.m_top_int, self.m_left_int + 1, f' { self.m_name_str.title() } ', self.m_inner_cols_int -3 , self._DARK_GRAY_AND_BLACK )

		# Draw content only if this list has items
		if len( self.m_items_list ) > 0 :
			# Get common width for every column
			# Start with o length list for holding the column width
			l_col_width_list = []
			# Start with 0 width
			for b_n in range( len( self.m_items_list[ 0 ] ) ) :
				l_col_width_list.append( 0 )
			# Compare value's length with widest yet
			for i_row_idx, i_row in enumerate( self.m_items_list ):
				for i_col_idx, col in enumerate( i_row ) :
					l_width_int = len( str( col ) )
					if l_width_int > l_col_width_list[ i_col_idx ] :
						l_col_width_list[ i_col_idx ] = l_width_int

			# Draw content of the list
			for idx in range( self.m_inner_lines_int ) :
				# Calculate list index
				list_idx = self.m_scroll_region_top_int + idx
				# Make sure selected index is within bounds
				if list_idx < 0 : break
				if list_idx >= len( self.m_items_list ) : break

				# Get row elements
				itm = ''
				if len( p_shown_cols ) == 1 :
					# Show exactly one field from the field id list
					itm += f'{ self.m_items_list[ list_idx ][ p_shown_cols[ 0 ] ] }'
				elif len( p_shown_cols ) > 1 :
					l_width_available = self.m_inner_cols_int - 2 - l_col_width_list[ p_shown_cols[ -1 ] ]
					for shown_idx_key, shown_idx_value in enumerate( p_shown_cols ) :
						# Store the value
						l_value = self.m_items_list[ list_idx ][ shown_idx_value ]
						if shown_idx_key != len( p_shown_cols ) - 1 :
							# What columns in list to show
							itm += f'{ l_value }'[ :l_width_available ].ljust( l_width_available )
						else :
							# What columns in list to show
							itm += f'{ l_value }'[ :l_col_width_list[ p_shown_cols[ -1 ] ] ].rjust( l_col_width_list[ p_shown_cols[ -1 ] ] )

				# Add padding
				itm = itm[ : self.m_inner_cols_int - 2 ].ljust( self.m_inner_cols_int - 2 )
				itm = ' ' + itm + ' '

				# Draw selection differently
				if list_idx == self.m_scroll_pointer_int and p_has_focus_bool :
					self.m_curses_win_obj.addnstr( 0 + idx, 0, itm, self.m_inner_cols_int, self._BLACK_AND_DARK_GRAY )
				else :
					self.m_curses_win_obj.addnstr( 0 + idx, 0, itm, self.m_inner_cols_int )

				if list_idx == self.m_selected_item_int :
					if p_has_focus_bool :
						self.m_curses_win_obj.addnstr( 0 + idx, 0, itm, self.m_inner_cols_int, curses.A_REVERSE )
					else :
						self.m_curses_win_obj.addnstr( 0 + idx, 0, itm, self.m_inner_cols_int, self._BLACK_AND_DARK_GRAY )
		else :
			# The list is empty
			self.m_curses_win_obj.addnstr( 0 , 1, 'Empty', self.m_inner_cols_int, self._DARK_GRAY_AND_BLACK )

		#self.m_curses_win_parent_obj.addstr( self.m_top_int - 1, self.m_left_int + 1, str( self.m_scroll_pointer_int ) )
		self.m_curses_win_obj.refresh()


	def select_item_pointed( self ) :
		if len( self.m_items_list ) > 0 and self.m_scroll_pointer_int != self.m_selected_item_int :
			self.m_selected_item_int = self.m_scroll_pointer_int
			return True
		else : return False


	def select_item_on_key( self, p_key_str, p_value ) :
		# Iterate through rows list
		for row_idx, row_dict in enumerate( self.m_items_list ) :
			# Check if key name exists in row
			if p_key_str in row_dict :
				self.m_curses_win_parent_obj.addstr( 0, 0, row_dict[ p_key_str ] )
				if row_dict[ p_key_str ] == p_value :
					self.select_item( self, row_idx )



	def select_item( self, p_item_idx_int ) :
		if p_item_idx_int > len( self.m_items_list ) - 1 : p_item_idx_int = len( self.m_items_list ) - 1
		if p_item_idx_int < 0 : p_item_idx_int = 0
		self.m_selected_item_int = p_item_idx_int
		self.m_scroll_pointer_int = p_item_idx_int

	def get_selected_item( self ) :
		if len( self.m_items_list ) > 0 :
			return self.m_items_list[ self.m_selected_item_int ]
		else : return None


	def scroll_rel( self, p_rel_pos_int  ) :
		# Only if list is not empty
		if len( self.m_items_list ) > 0 :
			self.m_scroll_pointer_int += p_rel_pos_int
			# Limits
			# Make sure that the scroll pointer does not go beyond list's last index
			if self.m_scroll_pointer_int > len( self.m_items_list ) - 1 :
				self.m_scroll_pointer_int = len( self.m_items_list ) - 1
			# Make sure that the scroll pointer does not go beyond list's first index ( 0 )
			if self.m_scroll_pointer_int < 0 :
				self.m_scroll_pointer_int = 0
			# Make sure that the scroll pointer does not go beyond list's first visible item
			if self.m_scroll_region_top_int > self.m_scroll_pointer_int :
				self.m_scroll_region_top_int = self.m_scroll_pointer_int
			# Make sure that the scroll pointer does not go beyond list's last visible item
			if self.m_scroll_region_top_int < self.m_scroll_pointer_int - ( self.m_inner_lines_int - 1 ) :
				self.m_scroll_region_top_int = self.m_scroll_pointer_int - ( self.m_inner_lines_int - 1 )
			if self.m_scroll_region_top_int < 0 : self.m_scroll_region_top_int = 0


	def add_item( self, p_new_item_obj ) :
		self.m_items_list.append( p_new_item_obj )
		if self.m_auto_scroll_bool :
			self.m_scroll_pointer_int = len( self.m_items_list ) - 1
			self.scroll_rel( 1 )


	def empty_list( self ) :
		self.m_items_list = []
		self.m_selected_item_int = -1
		self.m_scroll_region_top_int = 0
		self.m_scroll_pointer_int = 0
