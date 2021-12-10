import curses
from curses import wrapper
from app import App
from os import isatty, system
from time import strftime


# This prevents running the code when loading
if __name__ == '__main__' :
	app = App()
	wrapper( app.run )
	print( 'Reached the end of program.' )
	print( strftime( '%H:%M:%S') )
	if isatty( 0 ) : system( 'pause' )
