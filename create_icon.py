"""Vector-style shield icon rasterized locally; no online assets."""
from pathlib import Path
from PIL import Image, ImageDraw

folder = Path(__file__).parent / 'assets'
folder.mkdir(exist_ok=True)
im = Image.new('RGBA', (512, 512), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.rounded_rectangle((12, 12, 500, 500), radius=110, fill='#101725')
d.polygon([(256, 60), (427, 124), (408, 306), (347, 392), (256, 452), (165, 392), (104, 306), (85, 124)], fill='#51dfc0')
d.polygon([(256, 84), (401, 141), (384, 297), (329, 374), (256, 423), (183, 374), (128, 297), (111, 141)], fill='#192335')
d.rounded_rectangle((172, 227, 340, 344), radius=24, fill='#51dfc0')
d.arc((198, 135, 314, 281), 180, 360, fill='#51dfc0', width=23)
d.line([(198, 207), (198, 240)], fill='#51dfc0', width=23)
d.line([(314, 207), (314, 240)], fill='#51dfc0', width=23)
d.ellipse((242, 261, 270, 289), fill='#192335')
d.rounded_rectangle((249, 278, 263, 311), radius=6, fill='#192335')
im.save(folder / 'app.png')
im.save(folder / 'app.ico', sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
