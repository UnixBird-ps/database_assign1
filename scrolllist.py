import curses
from curses.textpad import rectangle


class ScrollList :
	def __init__( self, p_parent_window_obj, p_name_str, p_editable_bool, p_lines_int, p_cols_int, p_top_int, p_left_int ) :
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

		self.create_window( p_parent_window_obj )
		#self.m_curses_win_obj.scrollok( True )
		#self.m_curses_win_obj.idlok( 1 )


	def add_item( self, p_new_item_obj ) :
		self.m_items_list.append( p_new_item_obj )


	def create_window( self, p_parent ) :
		self.m_curses_win_parent_obj = p_parent
		self.m_curses_win_obj = p_parent.subwin( self.m_inner_lines_int + 1, self.m_inner_cols_int + 1, self.m_top_int + 1, self.m_left_int + 1 )


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


	def redraw_list( self, p_has_focus_bool, p_shown_cols = None ) :
		#if p_has_focus_bool :
		if p_shown_cols is None : p_shown_cols = []

		curses.init_pair( 1, curses.COLOR_WHITE, curses.COLOR_BLACK )
		curses.init_pair( 2, curses.COLOR_GREEN, curses.COLOR_BLACK )
		_WHITE_AND_BLACK = curses.color_pair( 1 )
		_GREEN_AND_BLACK = curses.color_pair( 2 )

		#self.m_curses_win_obj.border()

		if p_has_focus_bool : self.m_curses_win_parent_obj.attron( _GREEN_AND_BLACK )
		rectangle(
			self.m_curses_win_parent_obj,
			self.m_top_int,
			self.m_left_int,
			self.m_top_int + self.m_lines_int,
			self.m_left_int + self.m_cols_int
		)
		if p_has_focus_bool : self.m_curses_win_parent_obj.attroff( _GREEN_AND_BLACK )

		self.m_curses_win_parent_obj.addnstr( self.m_top_int, self.m_left_int + 2, self.m_name_str.title(), self.m_inner_cols_int )

		# find every col's width
		l_col_width_list = []
		for b_n in range( len( self.m_items_list[ 0 ] ) ): l_col_width_list.append( 0 )

		if len( self.m_items_list ) > 0 :
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
				self.m_curses_win_obj.addnstr( 0 + idx, 0, itm, self.m_inner_cols_int, _WHITE_AND_BLACK )
			else :
				self.m_curses_win_obj.addnstr( 0 + idx, 0, itm, self.m_inner_cols_int )

		#self.m_curses_win_parent_obj.addstr( self.m_top_int - 1, self.m_left_int + 1, str( self.m_scroll_pointer_int ) )

		self.m_curses_win_obj.refresh()


	def select_item_pointed( self ) :
		self.m_selected_item_int = self.m_scroll_pointer_int
