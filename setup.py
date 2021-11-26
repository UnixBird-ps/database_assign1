from dbutil import sqlite_check_table, sqlite_create_table, sqlite_run

def init_db( p_db_file_name_str ) :

	# Create the artists table
	if not sqlite_check_table( p_db_file_name_str, 'artists' ) :
		db_result = sqlite_create_table(
			p_db_file_name_str,
			'artists',
			'''
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name VARCHAR ( 100 ) NOT NULL,
			description VARCHAR ( 250 ) NOT NULL,
			UNIQUE ( name, description )
			'''
		)
		print( 'Table "artists" was ' + ( 'not', '' )[db_result] + 'created.' )


	# Create the albums table
	if not sqlite_check_table( p_db_file_name_str, 'albums' ) :
		db_result = sqlite_create_table(
			p_db_file_name_str,
			'albums',
			'''
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			title VARCHAR ( 100 ) NOT NULL,
			description VARCHAR ( 250 ) NOT NULL,
			year_released INTEGER,
			artist_id INTEGER,
			FOREIGN KEY ( artist_id ) REFERENCES artists ( id ),
			UNIQUE ( title, description, year_released, artist_id )
			'''
		)
		print( 'Table "albums" was', ( 'not', '' )[db_result] + 'created.' )


	# Create the songs table
	if not sqlite_check_table( p_db_file_name_str, 'songs' ) :
		db_result = sqlite_create_table(
			p_db_file_name_str,
			'songs',
			'''
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			name VARCHAR ( 100 ) NOT NULL,
			duration INTEGER NOT NULL,
			album_id INTEGER,
			FOREIGN KEY ( album_id ) REFERENCES albums ( id ),
			UNIQUE ( name, duration, album_id )
			'''
		)
		print( 'Table "songs" was', ( 'not', '' )[db_result] + 'created.' )


	# Create the artistsXalbums table

	# db_result = sqlite_create_table(
	# 	p_db_file_name_str,
	# 	'artistsXalbums',
	# 	'''
	# 	artist_id INTEGER NOT NULL,
	# 	album_id INTEGER NOT NULL,
	# 	FOREIGN KEY ( artist_id ) REFERENCES artists ( id ),
	# 	FOREIGN KEY ( album_id ) REFERENCES albums ( id ),
	# 	UNIQUE ( artist_id, album_id )
	# 	'''
	# )
	# print( 'Table "artistsXalbums" was', ( 'not', '' )[db_result] + 'created.' )


	# Create the albumsXsongs table

	# db_result = sqlite_create_table(
	# 	p_db_file_name_str,
	# 	'albumsXsongs',
	# 	'''
	# 	album_id INTEGER NOT NULL,
	# 	song_id INTEGER NOT NULL,
	# 	FOREIGN KEY ( album_id ) REFERENCES albums ( id ),
	# 	FOREIGN KEY ( song_id ) REFERENCES songs ( id ),
	# 	UNIQUE ( album_id, song_id )
	# 	'''
	# )
	# print( 'Table "albumsXsongs" was', ( 'not', '' )[db_result] + 'created.' )


	# Populate the artists table with initial values

	db_result = sqlite_run(
		p_db_file_name_str,
		'''
		INSERT INTO
			artists ( name, description )
		VALUES
			( 'Kansas', 'American rock band that became popular in the 1970s initially on album-oriented rock charts and later with hit singles such as "Carry On Wayward Son" and "Dust in the Wind"' ),
			( 'The Doors', 'American rock band formed in Los Angeles in 1965, with vocalist Jim Morrison, keyboardist Ray Manzarek, guitarist Robby Krieger, and drummer John Densmore' ),
			( 'America', 'A rock band that was formed in London in 1970 by Dewey Bunnell, Dan Peek, and Gerry Beckley. The trio met as sons of US Air Force personnel stationed in London, where they began performing live. Achieving significant popularity in the 1970s, the trio was famous for its close vocal harmonies and light acoustic folk rock sound. The band released a string of hit albums and singles, many of which found airplay on pop/soft rock stations' )
		ON CONFLICT DO NOTHING
		'''
	)
	if db_result[ 1 ] > 0 : print( 'Populated table "artists".' )


	# Populate the albums table with initial values

	db_result = sqlite_run(
		p_db_file_name_str,
		'''
		INSERT INTO
			albums ( title, description, year_released, artist_id )
		VALUES
			( 'Kansas', 'Debut studio album released by Kirshner in the United States and Epic Records in other countries', 1974, 1 ),
			( 'Song for America', 'Second studio album', 1975, 1 ),
			( 'Leftoverture', 'Fourth studio album. It was the band''s first album to be certified by the RIAA, and remains their highest selling album, having been certified 5 times platinum in the United States.', 1976, 1 ),
			( 'The Doors', 'Eponymous debut studio album recorded at Sunset Sound Recorders, Hollywood, California.', 1967, 2 ),
			( 'Strange Days', 'Second studio album, released by Elektra Records. Upon release, the album reached number three on the US Billboard 200, and eventually earned RIAA platinum certification.', 1967, 2 ),
			( 'Waiting for the Sun', 'Third studio album. Recorded at TTG Studios in Los Angeles, the album''s 11 tracks were recorded between February and May 1968 and the album was released by Elektra Records.', 1968, 2 ),
			( 'America', 'Debut studio album, released in 1971. It was initially released without "A Horse with No Name", which was released as a single in late 1971. When "A Horse with No Name" became a worldwide hit in early 1972, the album was re-released with that track.', 1971, 3 ),
			( 'Homecoming', 'Second studio album, released through Warner Bros. Records. Acoustic guitar-based, with a more pronounced electric guitar and keyboard section than their first album, their second effort helped continue the band''s success, and includes one of their best known hits, "Ventura Highway.', 1972, 3 ),
			( 'Hat Trick', 'third studio album by the American folk rock trio America, released on Warner Bros. Records in 1973.[2] It peaked at number 28 on the Billboard album chart; it failed to go gold, whereas the group''s first two releases had platinum sales.', 1973, 3 )
		ON CONFLICT DO NOTHING
		'''
	)
	if db_result[ 1 ] > 0 : print( 'Populated table "albums".' )


	# Populate the songs table with initial values

	db_result = sqlite_run(
		p_db_file_name_str,
		'''
		INSERT INTO
			songs ( name, duration, album_id )
		VALUES
			( 'Can I Tell You', 212, 1 ),
			( 'Bringing It Back', 213, 1 ),
			( 'Lonely Wind', 256, 1 ),
			( 'Belexes', 263, 1 ),
			( 'The Pilgrimage', 222, 1 ),
			( 'Aperçu', 594, 1 ),
			( 'Death of Mother Nature Suite', 463, 1 ),
			( 'Break On Through (To the Other Side)', 145, 2 ),
			( 'Soul Kitchen', 210, 2 ),
			( 'The Crystal Ship', 150, 2 ),
			( 'Twentieth Century Fox', 150, 2 ),
			( 'Alabama Song (Whiskey Bar)', 195, 2 ),
			( 'Light My Fire', 410, 2 ),
			( 'Back Door Man', 210, 2 ),
			( 'I Looked at You', 138, 2 ),
			( 'End of the Night', 169, 2 ),
			( 'Take It as It Comes', 133, 2 ),
			( 'The End', 695, 2 ),
			( 'Riverside', 183, 3 ),
			( 'Sandman', 308, 3 ),
			( 'Three Roses', 234, 3 ),
			( 'Children', 187, 3 ),
			( 'A Horse with No Name', 250, 3 ),
			( 'Here', 330, 3 ),
			( 'I Need You', 185, 3 ),
			( 'Rainy Day', 175, 3 ),
			( 'Never Found the Time', 230, 3 ),
			( 'Clarice', 241, 3 ),
			( 'Donkey Jaw', 317, 3 ),
			( 'Pigeon Song', 138, 3 )
	ON CONFLICT DO NOTHING
	''' )
	if db_result[ 1 ] > 0: print( 'Populated table "albums".' )
