import curses


class ScrollList :
	def __init__( self, p_parent_window_obj, p_name_str, p_editable_bool, p_top_int, p_left_int, p_height_int, p_width_int ) :
		self.m_name_str = p_name_str
		self.m_editable_bool = p_editable_bool
		self.m_items_list = []
		self.m_selected_item_int = 0
		self.m_top_int = p_top_int
		self.m_left_int = p_left_int
		self.m_height_int = p_height_int
		self.m_width_int = p_width_int
		self.m_curses_win_obj = None

		self.create_window( p_parent_window_obj )


	def add_item( self, p_new_item_obj ) :
		self.m_items_list.append( p_new_item_obj )


	def create_window( self, p_parent ) :
		self.m_curses_win_obj = p_parent.subwin( self.m_height_int, self.m_width_int, self.m_top_int, self.m_left_int )
