# -*- coding: utf-8 -*-

import wave
import struct
from scipy import fromstring, int16

# ファイルを読み出し
wavf = './output.wav'
wr = wave.open(wavf, 'r')

# waveファイルが持つ性質を取得
ch = wr.getnchannels()
width = wr.getsampwidth()
fr = wr.getframerate()
fn = wr.getnframes()

print("Channel: ", ch)
print("Sample width: ", width)
print("Frame Rate: ", fr)
print("Frame num: ", fn)
print("Params: ", wr.getparams())
print("Total time: ", 1.0 * fn / fr)

# waveの実データを取得し、数値化
data = wr.readframes(wr.getnframes())
wr.close()
X = fromstring(data, dtype=int16)
