import fontTools 
import glob
from fontTools.ttLib import TTFont
from pathlib import Path
from fontTools.ttLib.tables._g_l_y_f import Glyph
import subprocess
import shutil
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
import glob

BUILD = Path("build")

for ttf in BUILD.glob("*regular.ttf"):
#for ttf in ["build/gulim-regular.ttf"]:
	font = TTFont(ttf)
	cmapDict = font.getBestCmap()

	unicodes = []
	for entry in list(cmapDict.keys()):
		unicodes.append(hex(entry))

	unicodelist = str(unicodes)[1:-1].replace("', '",",")

	with open('build/glyphlist.txt', 'w') as f:
		for item in unicodes:
			f.write(item+",")

	subprocess.check_call(
	[
		"pyftsubset",
		ttf,
		"--unicodes-file=build/glyphlist.txt",
	]
	)