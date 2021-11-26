import sqlite3


def sqlite_check_table( p_db_file_name_str, p_table_name_str ) :
	l_sql_query_str =\
	f'''
	SELECT
		name
	FROM
		sqlite_master
	WHERE
		type = "table"
	AND
		name = "{ p_table_name_str }"
	'''
	# Open the database file ( create if not exists )
	l_dbcon = sqlite3.connect( p_db_file_name_str )
	l_dbcon.row_factory = sqlite3.Row
	# Open a cursor to the database
	l_cur = l_dbcon.cursor()
	# Execute query
	l_list_of_tables = l_cur.execute( l_sql_query_str ).fetchall()
	# Close connection
	l_dbcon.close()
	# Return True or False depending on success
	if len( l_list_of_tables ) > 0 :
		if p_table_name_str == l_list_of_tables[ 0 ][ 0 ] : return True
	return False


def	sqlite_create_table( p_db_file_name_str, p_table_name_str, p_field_defs_str ) :
	l_sql_query_str =\
	f'''
	CREATE TABLE IF NOT EXISTS
		{ p_table_name_str }
		(
		{ p_field_defs_str }
		)
	'''
	# Open the database file ( create if not exists )
	l_dbcon = sqlite3.connect( p_db_file_name_str )
	l_dbcon.row_factory = sqlite3.Row
	# Open a cursor to the database
	l_cur = l_dbcon.cursor()
	# Execute query
	l_cur.execute( l_sql_query_str )
	# Commit changes
	l_dbcon.commit()
	# Close connection
	l_dbcon.close()
	return sqlite_check_table( p_db_file_name_str, p_table_name_str )


def sqlite_dissect_table( p_db_file_name_str, p_table_name_str ) :
	# Open the database file ( create if not exists )
	l_dbcon = sqlite3.connect( p_db_file_name_str )
	l_dbcon.row_factory = sqlite3.Row
	# Open a cursor to the database
	l_cur = l_dbcon.cursor()
	l_sql_query_str =\
	f'''
	SELECT
		*
	FROM
		sqlite_master
	WHERE
		type = "table"
	AND
		name = "{ p_table_name_str }"
	'''
	# Execute query
	l_list_of_tables = l_cur.execute( l_sql_query_str ).fetchall()
	for idx_a, itm_a in enumerate( l_list_of_tables ) :
		print( f'{idx_a}  type:{type( itm_a )}  data:{itm_a}' )
		if type( itm_a ) == sqlite3.Row :
			for idx_b, itm_b in enumerate( itm_a ) :
				print( f'    {idx_b}  name:{l_cur.description[ idx_b ][ 0 ]}  data_type:{type( itm_b )}  value:{itm_b}' )
	# Close connection
	l_dbcon.close()


def sqlite_run( p_db_file_name_str, p_sql_query_str ) :
	# Open the database file ( create if not exists )
	l_dbcon = sqlite3.connect( p_db_file_name_str )
	# Open a cursor to the database
	l_cur = l_dbcon.cursor()
	# Execute query
	l_cur.execute( p_sql_query_str )
	# Commit changes
	l_dbcon.commit()
	# Close connection
	l_dbcon.close()
	l_cur_description = []
	if l_cur.description :
		for i_col in l_cur.description : l_cur_description.append( i_col[ 0 ] )
	# Return a list containing names of columns, number of rows affected
	l_db_results = []
	l_db_results.append( l_cur_description )
	l_db_results.append( l_cur.rowcount )
	l_db_results.append( [] )
	return l_db_results


def sqlite_get( p_db_file_name_str, p_sql_query_str, p_values = {} ) :
	# Open the database file ( create if not exists )
	l_dbcon = sqlite3.connect( p_db_file_name_str )
	l_dbcon.row_factory = sqlite3.Row
	# Open a cursor to the database
	l_cur = l_dbcon.cursor()
	# Execute query
	l_cur.execute( p_sql_query_str, p_values )
	# Get rows
	l_db_rows = l_cur.fetchall()
	# Close connection
	l_dbcon.close()
	# Create a list containing three lists, a list of column names, number of rows returned, and a list of data rows
	l_cur_description = []
	if l_cur.description :
		for b_col in l_cur.description : l_cur_description.append( b_col[ 0 ] )
	l_db_results = []
	l_db_results.append( l_cur_description )
	l_db_results.append( l_cur.rowcount )
	l_db_results.append( l_db_rows )
	# Return results to the caller
	return l_db_results


def sqlite_get_pretty( p_db_file_name_str, p_sql_query_str, p_values = {} ) :
	g_db_result = sqlite_get( p_db_file_name_str, p_sql_query_str, p_values )
	g_head_cols = g_db_result[ 0 ]
	g_col_width_list = [ ]
	for b_n in range( len( g_head_cols ) ): g_col_width_list.append( 0 )

	# put column header in the list
	g_rows = [ ]
	g_rows.append( tuple( g_head_cols ) )

	# put data rows in the list
	for b_i, b_row in enumerate( g_db_result[ 2 ] ):
		# if i >= 5: break
		g_rows.append( b_row )

	# find every col's width
	for i, row in enumerate( g_rows ):
		for ci, value in enumerate( row ):
			l = len( str( value ) )
			if l > g_col_width_list[ ci ]:
				g_col_width_list[ ci ] = l

	g_border_row_list = [ ]
	for c in g_col_width_list:
		g_border_row_list.append( '-' + '-' * c + '-' )

	g_border_row_str = '+' + '+'.join( g_border_row_list ) + '+'
	print( g_border_row_str )
	for i, row in enumerate( g_rows ):
		justified_row = [ ]
		for j, col in enumerate( row ):
			justified_row.append( str( col ).ljust( g_col_width_list[ j ] ) )
		table_row = '| ' + ' | '.join( justified_row ) + ' |'
		print( table_row )
		if i == 0: print( g_border_row_str )
	print( g_border_row_str )
