"""
アプリアイコン（icon.ico）を生成するスクリプト
実行: python create_icon.py
"""
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

import os
import struct
import zlib

def create_simple_ico():
    """Pillowなしでシンプルなicoファイルを生成"""
    # 32x32 の青い盾アイコンを簡易生成
    sizes = [256, 64, 32, 16]

    if HAS_PILLOW:
        images = []
        for size in sizes:
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            # 背景円
            draw.ellipse([2, 2, size-2, size-2], fill=(5, 11, 24, 255))
            # 外枠
            draw.ellipse([2, 2, size-2, size-2], outline=(0, 229, 255, 255), width=max(1, size//20))
            # M 文字
            margin = size // 5
            cx, cy = size // 2, size // 2
            font_size = size * 2 // 5
            try:
                draw.text((margin, margin), "M", fill=(0, 229, 255, 255))
            except Exception:
                pass
            images.append(img)

        images[0].save(
            'icon.ico',
            format='ICO',
            sizes=[(s, s) for s in sizes]
        )
        print("icon.ico を生成しました（Pillow使用）")
    else:
        # 最小限のICOファイルをバイナリで生成（16x16 青色）
        import struct
        width = height = 16
        # BMP ヘッダー付きの単純な青いアイコン
        pixel = b'\x1a\x05\x00\xff'  # RGBA: dark blue
        highlight = b'\x00\xe5\xff\xff'  # RGBA: cyan

        pixels = []
        for y in range(height):
            row = []
            for x in range(width):
                if (x == 0 or x == width-1 or y == 0 or y == height-1):
                    row.append(highlight)
                else:
                    row.append(pixel)
            pixels.extend(row)

        bmp_data = b''.join(pixels)

        # ICO ファイル形式
        ico_header = struct.pack('<HHH', 0, 1, 1)  # reserved, type=1(ico), count=1
        img_header = struct.pack('<BBBBHHII',
            width, height, 0, 0,
            1, 32,  # planes, bit_count
            len(bmp_data) + 40,  # size of image data
            6 + 16  # offset to image data
        )

        # DIB header (BITMAPINFOHEADER)
        dib = struct.pack('<IiiHHIIiiII',
            40,  # header size
            width, -height,  # width, height (negative = top-down)
            1, 32,  # planes, bit count
            0,  # compression (BI_RGB)
            len(bmp_data),  # image size
            0, 0,  # X/Y pixels per meter
            0, 0   # colors used/important
        )

        with open('icon.ico', 'wb') as f:
            f.write(ico_header)
            f.write(img_header)
            f.write(dib)
            f.write(bmp_data)

        print("icon.ico を生成しました（シンプル版）")

if __name__ == '__main__':
    create_simple_ico()
    if os.path.exists('icon.ico'):
        print(f"完了: {os.path.getsize('icon.ico')} bytes")
