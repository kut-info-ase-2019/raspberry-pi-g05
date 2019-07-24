# -*- coding: utf-8 -*-

import wave
import struct
from scipy import fromstring, int16
from scipy.io.wavfile import read
import numpy as np

# 閾値の定義
THRESHOLD = 0.01

# ファイルを読み出し
wavf = './output.wav'
wr = wave.open(wavf, 'r')

# waveファイルが持つ性質を取得
ch = wr.getnchannels()
width = wr.getsampwidth()
fr = wr.getframerate()
fn = wr.getnframes()
amp = (2**8) ** width / 2

#print("Channel: ", ch)
#print("Sample width: ", width)
#print("Frame Rate: ", fr)
#print("Frame num: ", fn)
#print("Params: ", wr.getparams())
#print("Total time: ", 1.0 * fn / fr)

# waveの実データを取得し、数値化
data = wr.readframes(wr.getnframes())
wr.close()
X = np.frombuffer(data, 'int16') # intに変換
X_amp = X / amp # 振幅の正規化
count = 0
for num in range(fn):
	if X_amp[num] > THRESHOLD:
		count = count + 1
print(count/fn * 100, "%")
#print(max(X),min(X))
#print(max(X_amp), min(X_amp))
