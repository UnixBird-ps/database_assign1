from curses import wrapper
from app import main
from os import isatty, system

# Run only when started as standalone
# This prevents running the code when loading
if __name__ == '__main__':
	wrapper( main )
	print( 'Reached the end of program.' )
	if isatty( 0 ) : system( 'pause' )
