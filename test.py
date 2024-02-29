import fontTools 
import glob
from fontTools.ttLib import TTFont
from pathlib import Path
from fontTools.ttLib.tables._g_l_y_f import Glyph
import subprocess
import shutil
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
import glob
import fontTools.ttLib.tables.E_B_L_C_
import fontTools.ttLib.tables.E_B_D_T_

BUILD = Path("build")

def checkConsecutive(l):
    return sorted(l) == list(range(min(l), max(l)+1))

#for t in BUILD.glob("*subset.ttf"):
for t in [Path("build/gulim-regular.subset.ttf")]:
	ttf = str(t)
	fontName = ttf.split("/")[1].split("-")[0]
	font = TTFont(ttf)
	originalFont = TTFont(ttf.replace(".subset",""))

	subsetCMAP = list(font.getBestCmap().values())

	# We will create a new EBLC with the same set of strikes as the old, but with different subtables.
	old_EBLC = originalFont["EBLC"]

	EBLC = originalFont["EBLC"]
	EBDT = originalFont["EBDT"]

	for s,strike in enumerate(EBLC.strikes):
		print (fontName,"- Processing strike",s)
	
		tableRemove = []
		namesRequired = []

		print (fontName,"- Stripping unnecessary tables from EBLC strike")
		for i,table in enumerate(strike.indexSubTables):
			if table.names[0] in subsetCMAP:
				for name in table.names: 
					namesRequired.append(name)
			# elif "gulim" in ttf and table.names[0] == "glyph40194": #this table is non-unicode and needs special casing
			# 	for name in table.names: 
			# 		namesRequired.append(name)
			# elif "dotum" in ttf and table.names[0] == "glyph52011": #this table is non-unicode and needs special casing
			# 	for name in table.names: 
			# 		namesRequired.append(name)
			else:
				tableRemove.append(i)

		for id in reversed(tableRemove): #now that we have a list of tables to remove, we remove them!
			del strike.indexSubTables[id]

		print (fontName,"- Stripping unnecessary data from EBDT strikeData")
		# After documenting all of the glyphs present in the strike, we remove any data that isn't relavent. 
		for entry in list(EBDT.strikeData[s].keys()):
			if entry not in namesRequired:
				del EBDT.strikeData[s][entry]

	print (fontName,"- Done processing strikes")
	print (fontName,"- Generating font")

	for s,strike in enumerate(EBLC.strikes):
		for t,table in enumerate(strike.indexSubTables):
			GID = []
			for name in table.names:
				GID.append(font.getGlyphID(name))
			is_consecutive = checkConsecutive(GID)
			if is_consecutive == False:
				print ("Strike",s,"table",t,"is False")
				print (GID)

	font["EBDT"] = EBDT #Gotta add this first or BOOM
	font["EBLC"] = EBLC

	font.save("../fonts/bitmap/"+ttf.split("/")[1].replace(".subset",""))
