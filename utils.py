from inspect import getframeinfo, stack


def debug_info( p_msg = '' ) :
	"""
	Outputs the name of the source code file and the line number where the message is sent from
	Used only for debugging
	:param    p_msg: string
	:return:  nothing
	"""
	l_caller = getframeinfo( stack()[ 1 ][ 0 ] )
	print( f'Debug info: in file "{ l_caller.filename }", at line { l_caller.lineno }: { p_msg }' )
