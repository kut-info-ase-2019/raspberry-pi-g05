# -*- coding: utf-8 -*-
import wave
import numpy as np
import matplotlib.pyplot as plt

wf = wave.open("test.wav" , "r" )
buf = wf.readframes(wf.getnframes())

# バイナリデータを整数型（16bit）に変換
data = np.frombuffer(buf, dtype="int16")

f = open('test.txt', 'w') # 書き込みモードで開く
for i in data:
	#print(i)
	f.write(str(i) + "\n") # 引数の文字列をファイルに書き込む

f.close() # ファイルを閉じる

# グラフ化
plt.plot(data)
plt.grid()
plt.show()
