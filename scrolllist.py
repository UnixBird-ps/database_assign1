import curses
from curses.textpad import rectangle
from utils import debug_info



class ScrollList( object ) :

	def __init__( self, p_parent_window_obj, p_name, p_editable_bool, p_lines_int, p_cols_int, p_top_int, p_left_int, p_auto_scroll_bool, options = None ) :
		# Holds minimums of column's width
		self.m_col_widths_list = []
		# Holds indices of visible columns
		self.m_vis_cols_list = []
		# Holds labels of visible columns
		self.m_col_labels_list = []
		self.m_justify_list = []
		# Holds a list of keyboard keys to be ignored by callers getkey()
		self.m_disabled_keys_list = []

		self.m_name = p_name

		#debug_info( f'\nScrollList "{ self.m_name }" constructor options:' )
		#print( options )

		#debug_info( f'\nScrollList "{ self.m_name }" attributes:' )

		# If options param was specified and is a dict
		if options is not None and isinstance( options, dict ) :
			# If options contains a key named 'vis_cols_list' that is a list
			if 'vis_cols_list' in list( options.keys() ) and isinstance( options.get( 'vis_cols_list' ), list ):
				# Get it's values
				self.m_vis_cols_list = options.get( 'vis_cols_list' )
				# Ensure that vis_col_val is within bounderies of column width list
				l_len_diff = max( self.m_vis_cols_list ) + 1 - len( self.m_col_widths_list )
				if l_len_diff > 0 :
					self.m_col_widths_list.extend( [ 0 ] * l_len_diff )

			if 'col_labels_list' in list( options.keys() ) and isinstance( options.get( 'col_labels_list' ), list ) :
				self.m_col_labels_list = options.get( 'col_labels_list' )
				# Set width of visible columns only
				# Select item on index from vis cols list
				for col_label_itr, col_label_val in enumerate( self.m_col_labels_list ) :
					# Set width for columns corresponding to visible column
					if 0 < col_label_itr < len( self.m_vis_cols_list ) - 1 :
						self.m_col_widths_list[ self.m_vis_cols_list[ col_label_itr ] ] = 1 + len( col_label_val )
						print( f'self.m_col_widths_list[]: { self.m_col_widths_list }' )
					else :
						self.m_col_widths_list[ self.m_vis_cols_list[ col_label_itr ] ] = len( col_label_val )

			if 'justify_list' in list( options.keys() ) and isinstance( options.get( 'justify_list' ), list ):
				self.m_justify_list = options.get( 'justify_list' )

			if 'disabled_keys_list' in list( options.keys() ) and isinstance( options.get( 'disabled_keys_list' ), list ) :
				self.m_disabled_keys_list = options.get( 'disabled_keys_list' )

		#print( 'm_vis_cols_list:', self.m_vis_cols_list )
		#print( 'm_col_widths_list:', self.m_col_widths_list )
		#print( 'm_col_labels_list:', self.m_col_labels_list )
		#print( 'm_justify_list:', self.m_justify_list )
		#print( 'm_disabled_keys_list:', self.m_disabled_keys_list )

		# Get the size of the screen
		l_scr_size_yx = p_parent_window_obj.getmaxyx()

		p_top_int = max( 0, p_top_int )
		p_left_int = max( 0, p_left_int )
		self.m_top_int = p_top_int
		self.m_left_int = p_left_int
		p_lines_int = max( 3, p_lines_int )
		p_cols_int = max( 3, p_cols_int )
		p_lines_int = min( l_scr_size_yx[ 0 ] - p_top_int, p_lines_int )
		p_cols_int = min( l_scr_size_yx[ 1 ] - p_left_int, p_cols_int )
		self.m_lines_int = p_lines_int
		self.m_cols_int = p_cols_int
		self.m_inner_lines_int = p_lines_int - 1 - 1
		self.m_inner_cols_int = p_cols_int - 1
		self.m_items_list = []
		self.m_editable_bool = p_editable_bool
		self.m_selected_item_int = -1
		self.m_scroll_region_top_int = 0
		self.m_scroll_pointer_int = 0
		self.m_auto_scroll_bool = p_auto_scroll_bool

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



	def get_name( self ) :
		return self.m_name



	def create_window( self, p_parent ) :
		self.m_curses_win_parent_obj = p_parent
		self.m_curses_win_obj = p_parent.subwin( self.m_inner_lines_int + 1, self.m_inner_cols_int + 1, self.m_top_int + 1, self.m_left_int + 1 )



	def redraw_list( self, p_has_focus_bool ) :#, p_options_dict = None ) :
		"""
		Draws a border around the list
		Outputs visible items of the list
		:param p_has_focus_bool:
		:return:
		"""
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
			self.m_curses_win_parent_obj.addnstr( self.m_top_int, self.m_left_int + 1, f' { self.m_name.title() } ', self.m_inner_cols_int - 3, self._LIGHT_GREEN_AND_BLACK )
		else :
			self.m_curses_win_parent_obj.addnstr( self.m_top_int, self.m_left_int + 1, f' { self.m_name.title() } ', self.m_inner_cols_int -3 , self._DARK_GRAY_AND_BLACK )

		# Output content only if this list has items
		if len( self.m_items_list ) <= 0 :
			# The list is empty
			self.m_curses_win_obj.addnstr( 0 , 1, 'Empty', self.m_inner_cols_int, self._DARK_GRAY_AND_BLACK )
		else :
			# Write column names on first line of the window
			new_row_str = ''
			l_width_available = self.m_inner_cols_int - 2 # - self.m_col_widths_list[ l_shown_cols_list[ -1 ] ]
			#for col_labels_list_itr, col_labels_list_val in enumerate( self.m_col_labels_list ) :
			for vis_col_itr, vis_col_val in enumerate( self.m_vis_cols_list ) :
				l_col_labels_list_val = self.m_col_labels_list[ vis_col_itr ]
				# print( 'col_labels_list_itr:', col_labels_list_itr )
				# print( 'col_labels_list_val:', col_labels_list_val )
				# print( 'm_vis_cols_list[ col_labels_list_itr ]', self.m_vis_cols_list[ col_labels_list_itr ] )
				new_row_str += l_col_labels_list_val[ :self.m_col_widths_list[ vis_col_val ] ].ljust( self.m_col_widths_list[ vis_col_val ] )
			# Add padding to column labels
			new_row_str = new_row_str[ : l_width_available ].ljust( l_width_available )
			new_row_str = '<' + new_row_str + '>'
			self.m_curses_win_obj.addnstr( 0, 0, new_row_str, self.m_inner_cols_int, self._DARK_GRAY_AND_BLACK )
			#print( 'Col label string: ', new_row_str )

			# # Get common width for every column
			# Start with 0 width
			#self.m_col_widths_list = [ 0 ] * len( self.m_items_list[ 0 ] )
			# Compare value's length with widest yet
			# debug_info( f'\nScrollList "{ self.m_name }" redraw:' )
			# for row_itr, row_val in enumerate( self.m_items_list ):
			# 	#print( f'type(row_val): { type( row_val ) }  row_val:{ row_val }' )
			# 	for field_itr, field_val in enumerate( row_val.values() ) :
			# 		print( f'type( field_val ): { type( field_val ) }  field_val: { field_val }' )
			# 		self.m_col_widths_list[ field_itr ] = max( self.m_col_widths_list[ field_itr ], len( str( field_val ) ) )

			# Draw content of the list
			for itr in range( self.m_inner_lines_int ) :
				# Calculate list index
				item_idx = self.m_scroll_region_top_int + itr
				# Make sure selected index is within bounds
				if item_idx < 0 : break
				if item_idx >= len( self.m_items_list ) : break
				# Get row elements
				new_row_str = ''
				l_list_row_dict = self.m_items_list[ item_idx ]
				if len( self.m_vis_cols_list ) == 1 :
					# Show exactly one field from the field id list
					new_row_str += f'{ l_list_row_dict.get( list( l_list_row_dict )[ self.m_vis_cols_list[ 0 ] ] ) }'
				elif len( self.m_vis_cols_list ) > 1 :
					# Make room for last field
					l_width_available = self.m_inner_cols_int - 2 # - self.m_col_widths_list[ l_shown_cols_list[ -1 ] ]
					for vis_col_itr, vis_col_val in enumerate(self.m_vis_cols_list ) : # reversed(
						# Store the value
						l_dict_key = list( l_list_row_dict.keys() )[ vis_col_val ]
						l_value = str( l_list_row_dict[ l_dict_key ] )
						l_justify_value = list(self.m_justify_list )[ vis_col_itr ] # reversed(
						# if vis_col_itr != len( self.m_vis_cols_list ) - 1 :
						# What columns in list to show
						match l_justify_value :
							case 'left' :
								new_row_str = f'{ l_value }'[ :self.m_col_widths_list[ vis_col_val ] ].ljust( self.m_col_widths_list[ vis_col_val ] ) + new_row_str
							case 'right' :
								new_row_str = new_row_str + f'{ l_value }'[ :self.m_col_widths_list[ vis_col_val ] ].rjust( self.m_col_widths_list[ vis_col_val ] )
							case 'center' :
								new_row_str = f'{ l_value }'[ :self.m_col_widths_list[ vis_col_val ] ].center( self.m_col_widths_list[ vis_col_val ] ) + new_row_str
						# else :
						# 	# Last column is special, which will be actually the first because the loop is reversed
						# 	# itm += f'{ l_value }'[ :self.m_col_widths_list[ l_shown_cols_list[ -1 ] ] ].rjust( self.m_col_widths_list[ l_shown_cols_list[ -1 ] ] )
						# 	new_row_str = f'{ l_value }'[ :l_width_available - len( new_row_str )].ljust( l_width_available - len( new_row_str ) ) + new_row_str


				# Add padding
				new_row_str = new_row_str[ : self.m_inner_cols_int - 2 ].ljust( self.m_inner_cols_int - 2 )
				new_row_str = ' ' + new_row_str + ' '

				# Draw selection differently
				if item_idx == self.m_scroll_pointer_int and p_has_focus_bool :
					self.m_curses_win_obj.addnstr( 1 + itr, 0, new_row_str, self.m_inner_cols_int, self._BLACK_AND_DARK_GRAY )
				else :
					self.m_curses_win_obj.addnstr( 1 + itr, 0, new_row_str, self.m_inner_cols_int )

				if item_idx == self.m_selected_item_int :
					if p_has_focus_bool :
						self.m_curses_win_obj.addnstr( 1 + itr, 0, new_row_str, self.m_inner_cols_int, curses.A_REVERSE )
					else :
						self.m_curses_win_obj.addnstr( 1 + itr, 0, new_row_str, self.m_inner_cols_int, self._BLACK_AND_DARK_GRAY )

		self.m_curses_win_obj.refresh()



	def select_item_pointed( self ) :
		if len( self.m_items_list ) > 0 and self.m_scroll_pointer_int != self.m_selected_item_int :
			self.m_selected_item_int = self.m_scroll_pointer_int
			return True
		else : return False



	def select_item_on_dict( self, p_selection_dict ) :
		# Iterate through rows list
		for row_itr, row_dict in enumerate( self.m_items_list ) :
			l_found = True

			# check every key in p_selection_pair_dict if it is in the keys of the list row
			# 1. For every pair in p_selection_dict check if a key of that pair exist in list row
			for pair_itr in range( len( p_selection_dict ) ) :
				l_selection_dict_key   = list( p_selection_dict )[ pair_itr ]
				l_selection_dict_value = p_selection_dict[ l_selection_dict_key ]
				# 2. Check if key name exists in list row
				if l_selection_dict_key in row_dict.keys() :
					if l_selection_dict_value != row_dict[ l_selection_dict_key ] :
						# This value is not equal to the value if same key in p_selection_dict
						l_found = False
					else :
						l_found = l_found and True
			# Select that row if it contains the values in p_selection_dict
			if l_found :
				self.select_item( row_itr )
				break



	def select_item( self, p_item_idx_int ) :
		if len( self.m_items_list ) > 0 :
			if p_item_idx_int > len( self.m_items_list ) - 1 : p_item_idx_int = len( self.m_items_list ) - 1
			if p_item_idx_int < 0 : p_item_idx_int = 0
			self.m_selected_item_int = p_item_idx_int
			self.m_scroll_pointer_int = p_item_idx_int



	def select_first( self ) :
		if len( self.m_items_list ) > 0 :
			self.m_selected_item_int = 0
			self.m_scroll_pointer_int = 0



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
			self.m_selected_item_int = self.m_scroll_pointer_int



	def add_item( self, p_new_item_dict ) :
		"""
		Appends specified dict to the list
		Keeps the last item visible if that option was specified at the this object's creation
		:param   dict p_new_item_dict:  Data to be append
		:return:
		"""
		# Append new item
		self.m_items_list.append( p_new_item_dict )

		#debug_info( f'ScrollList "{ self.m_name }" add item:' )
		#print( f'p_new_item_dict.values(): { p_new_item_dict.values() }' )
		#print( f'before: { self.m_col_widths_list }' )

		# Ensure the size of col_widths_list is large enough
		l_len_diff = len( p_new_item_dict ) - len( self.m_col_widths_list )
		if l_len_diff > 0 :
			self.m_col_widths_list.extend( [ 0 ] * l_len_diff )

		#print( f'type( p_new_item_dict         ): { type( p_new_item_dict         ) }  p_new_item_dict: { p_new_item_dict }' )
		#print( f'type( self.m_items_list[ -1 ] ): { type( self.m_items_list[ -1 ] ) }          row_val: { self.m_items_list[ -1 ] }' )

		# Adjust widest common field width
		# for column_itr, column_width_val in enumerate( self.m_col_widths_list ) :
		# 	self.m_col_widths_list[ column_itr ] = max( self.m_col_widths_list[ column_itr ], len( str( p_new_item_dict[ list( p_new_item_dict.keys() )[ column_itr ] ] ) ) )
		for field_itr, field_val in enumerate( p_new_item_dict.values() ) :
			#print( f'type( field_val ): { type( field_val ) }  field_val: { field_val }' )
			#self.m_col_widths_list[ field_itr ] = max( self.m_col_widths_list[ field_itr ], 1 + len( str( field_val ) ) )
			self.m_col_widths_list[ field_itr ] = max( self.m_col_widths_list[ field_itr ], len( str( field_val ) ) )

		#print( f' after: { self.m_col_widths_list }' )

		# Scroll this list to show the appended item if autoscroll is enabled
		if self.m_auto_scroll_bool :
			self.m_scroll_pointer_int = len( self.m_items_list ) - 1
			self.scroll_rel( 1 )



	def empty_list( self ) :
		"""
		Removes all items in the list, resets selection, scroll position and list of widest common field width
		:return: Nothing
		"""
		self.m_items_list = []
		self.m_selected_item_int = -1
		self.m_scroll_region_top_int = 0
		self.m_scroll_pointer_int = 0
		# Reset widest common width for all columns
		self.m_col_widths_list = [ 0 for x in range( len( self.m_col_widths_list ) ) ]

		for col_label_itr, col_label_val in enumerate( self.m_col_labels_list ) :
			# Set width for columns corresponding to visible column
			if col_label_itr < len( self.m_vis_cols_list ) :
				self.m_col_widths_list[ self.m_vis_cols_list[ col_label_itr ] ] = len( col_label_val )
