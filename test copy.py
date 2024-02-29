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

#for t in BUILD.glob("*subset.ttf"):
for t in [Path("build/gulim-regular.subset.ttf")]:
	ttf = str(t)
	fontName = ttf.split("/")[1].split("-")[0]
	font = TTFont(ttf)
	originalFont = TTFont(ttf.replace(".subset",""))

	subsetCMAP = list(font.getBestCmap().values())

	# We will create a new EBLC with the same set of strikes as the old, but with different subtables.
	old_EBLC = originalFont["EBLC"]

	EBLC = fontTools.ttLib.newTable("EBLC")
	EBDT = originalFont["EBDT"]
	EBLC.strikes = []

	for s,strike in enumerate(old_EBLC.strikes):
		print (fontName,"- Processing strike",s)
		#create a new strike in the new table
		EBLC.strikes.append(fontTools.ttLib.tables.E_B_L_C_.Strike())
	
		#Now we check which tables are required for the new EBLC table (note some might be missing due to only containing non-CMAP glyphs)
		tablesRequired = []
		namesRequired = []
		for i,table in enumerate(strike.indexSubTables):
			for name in table.names:
				if name in subsetCMAP and i not in tablesRequired:
					for name in table.names: # record all names in the required table
						namesRequired.append(name)
					tablesRequired.append(i) #I figured we only need to verify 1 glyph
				elif "gulim" in ttf and name == "glyph40194":
					tablesRequired.append(i) # There's a table which only has non-unicodes
					for name in table.names: # record all names in the required table
						namesRequired.append(name)
				elif "dotum" in ttf and name == "glyph53567":
					tablesRequired.append(i) # There's a table which only has non-unicodes
					for name in table.names: # record all names in the required table
						namesRequired.append(name)

		print (fontName,"- Adding subtables to new strike in EBLC")
		# Once we've figured out which tables need to be kept, we add those tables to the new EBLC
		EBLC.strikes[len(EBLC.strikes)-1].bitmapSizeTable = strike.bitmapSizeTable
		for id in tablesRequired:
			EBLC.strikes[len(EBLC.strikes)-1].indexSubTables.append(strike.indexSubTables[id])

		print (fontName,"- Stripping unnecessary data from strikeData in EBDT")
		# After documenting all of the glyphs present in the strike, we remove any data that isn't relavent. 
		for entry in list(EBDT.strikeData[s].keys()):
			if entry not in namesRequired:
				del EBDT.strikeData[s][entry]

	print (fontName,"- Done processing strikes")
	print (fontName,"- Generating font")

	font["EBLC"] = EBLC
	font["EBDT"] = EBDT

	font.save("../fonts/bitmap/"+ttf.split("/")[1].replace(".subset",""))
