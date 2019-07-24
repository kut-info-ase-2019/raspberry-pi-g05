# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import pyaudio
import wave

# 湿度温度センサーで使用するPIN
#DHT11 connect to BCM_GPIO14
DHTPIN = 14
# set GPIO 0 as LED pin
LEDPINGREEN     = 5
LEDPINYELLOW    = 7
LEDPINRED       = 9

#GPIO.setmode(GPIO.BCM)

MAX_UNCHANGE_COUNT = 100

STATE_INIT_PULL_DOWN = 1
STATE_INIT_PULL_UP = 2
STATE_DATA_FIRST_PULL_DOWN = 3
STATE_DATA_PULL_UP = 4
STATE_DATA_PULL_DOWN = 5

# 超音波センサーで使用するPIN
GPIO_TRIG = 26
GPIO_ECHO = 19

# 録音
CHUNK = 1024 * 2
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "output.wav"

# 初期化
#setup function for some setup---custom function
def setup():
	# 湿度温度センサー
	GPIO.setwarnings(False)
	#set the gpio modes to BCM numbering
	GPIO.setmode(GPIO.BCM)
	#set LEDPIN's mode to output,and initial level to LOW(0V)
	GPIO.setup(LEDPINGREEN,GPIO.OUT,initial=GPIO.LOW)
	GPIO.setup(LEDPINYELLOW,GPIO.OUT,initial=GPIO.LOW)
	GPIO.setup(LEDPINRED,GPIO.OUT,initial=GPIO.LOW)

	# 距離センサー
	#"""
	#初期化します
	#:param trig: Trigger用ピン番号、またはGPIO 番号
	#:param echo: Echo用ピン番号、またはGPIO 番号
	#:param mode: GPIO.BCM、または GPIO.BOARD (default:GPIO.BCM)
	#:return: なし
	#"""
	GPIO.setup(GPIO_TRIG, GPIO.OUT)
	GPIO.setup(GPIO_ECHO, GPIO.IN)

# 温度と湿度を取る
def read_dht11_dat():
	GPIO.setup(DHTPIN, GPIO.OUT)
	GPIO.output(DHTPIN, GPIO.HIGH)
	time.sleep(0.05)
	GPIO.output(DHTPIN, GPIO.LOW)
	time.sleep(0.02)
	GPIO.setup(DHTPIN, GPIO.IN, GPIO.PUD_UP)

	unchanged_count = 0
	last = -1
	data = []
	while True:
		current = GPIO.input(DHTPIN)
		data.append(current)
		if last != current:
			unchanged_count = 0
			last = current
		else:
			unchanged_count += 1
			if unchanged_count > MAX_UNCHANGE_COUNT:
				break

	state = STATE_INIT_PULL_DOWN

	lengths = []
	current_length = 0

	for current in data:
		current_length += 1

		if state == STATE_INIT_PULL_DOWN:
			if current == GPIO.LOW:
				state = STATE_INIT_PULL_UP
			else:
				continue
		if state == STATE_INIT_PULL_UP:
			if current == GPIO.HIGH:
				state = STATE_DATA_FIRST_PULL_DOWN
			else:
				continue
		if state == STATE_DATA_FIRST_PULL_DOWN:
			if current == GPIO.LOW:
				state = STATE_DATA_PULL_UP
			else:
				continue
		if state == STATE_DATA_PULL_UP:
			if current == GPIO.HIGH:
				current_length = 0
				state = STATE_DATA_PULL_DOWN
			else:
				continue
		if state == STATE_DATA_PULL_DOWN:
			if current == GPIO.LOW:
				lengths.append(current_length)
				state = STATE_DATA_PULL_UP
			else:
				continue
	if len(lengths) != 40:
		print ("Data not good, skip\n")
		return False

	shortest_pull_up = min(lengths)
	longest_pull_up = max(lengths)
	halfway = (longest_pull_up + shortest_pull_up) / 2
	bits = []
	the_bytes = []
	byte = 0

	for length in lengths:
		bit = 0
		if length > halfway:
			bit = 1
		bits.append(bit)
	print ('bits: %s, length: %d' % (bits, len(bits)))
	for i in range(0, len(bits)):
		byte = byte << 1
		if (bits[i]):
			byte = byte | 1
		else:
			byte = byte | 0
		if ((i + 1) % 8 == 0):
			the_bytes.append(byte)
			byte = 0
	print (the_bytes)
	checksum = (the_bytes[0] + the_bytes[1] + the_bytes[2] + the_bytes[3]) & 0xFF
	if the_bytes[4] != checksum:
		print ('Data not good, skip\n')
		return False

	return the_bytes[0], the_bytes[2]

def main():
	while True:
		record()
		print ("距離：{0} cm".format(get_distance()))
		t = time.sleep(1)
		#print (t)
		result = read_dht11_dat()
		if result:
			humidity, temperature = result
			print ('humidity: %s %%,  Temperature: %s C' % (humidity, temperature))
			heat_index = 0.81*temperature + 0.01*humidity*(0.99*temperature - 14.3) + 46.3
			print ('heat index: %s\n' % heat_index)
		time.sleep(2)

#define a destroy function for clean up everything after the script finished
def destroy():
	#turn off LED
	GPIO.output(LEDPIN,GPIO.LOW)
	#release resource
	GPIO.cleanup()

# 超音波センサー
def pulse_in(pin, value=GPIO.HIGH, timeout=1.0):
	"""
	ピンに入力されるパルスを検出します。
	valueをHIGHに指定した場合、pulse_in関数は入力がHIGHに変わると同時に時間の計測を始め、
	またLOWに戻るまでの時間(つまりパルスの長さ)をマイクロ秒単位(*1)で返します。
	タイムアウトを指定した場合は、その時間を超えた時点で0を返します。
	*1 pythonの場合はtimeパッケージの仕様により実装依存ですが、概ねnanosecで返ると思います。
	:param pin: ピン番号、またはGPIO 番号(GPIO.setmodeに依存。)
	:param value: パルスの種類(GPIO.HIGH か GPIO.LOW。default:GPIO.HIGH)
	:param timeout: タイムアウト(default:1sec)
	:return: パルスの長さ（秒）タイムアウト時は0
	"""
	start_time = time.time()
	not_value = (not value)

	# 前のパルスが終了するのを待つ
	while GPIO.input(pin) == value:
		if time.time() - start_time > timeout:
			return 0

	# パルスが始まるのを待つ
	while GPIO.input(pin) == not_value:
		if time.time() - start_time > timeout:
			return 0

	# パルス開始時刻を記録
	start = time.time()

	# パルスが終了するのを待つ
	while GPIO.input(pin) == value:
		if time.time() - start_time > timeout:
			return 0

	# パルス終了時刻を記録
	end = time.time()

	return end - start

def get_distance(temp=15):
	"""
	距離を取得します。取得に失敗した場合は0を返します。
	:param trig: Trigger用ピン番号、またはGPIO 番号(GPIO.setmodeに依存。)(GPIO.OUT)
	:param echo: Echo用ピン番号、またはGPIO 番号(GPIO.setmodeに依存。)(GPIO.IN)
	:param temp: 取得可能であれば温度(default:15℃)
	:return: 距離（ｃｍ）タイムアウト時は 0
	"""

	# 出力を初期化
	GPIO.output(GPIO_TRIG, GPIO.LOW)
	time.sleep(0.3)
	# 出力(10us以上待つ)
	GPIO.output(GPIO_TRIG, GPIO.HIGH)
	time.sleep(0.000011)
	# 出力停止
	GPIO.output(GPIO_TRIG, GPIO.LOW)

	# echo からパルスを取得
	dur = pulse_in(GPIO_ECHO, GPIO.HIGH, 1.0)

	# ( パルス時間 x 331.50 + 0.61 * 温度 ) x (単位をcmに変換) x 往復
	# return dur * (331.50 + 0.61 * temp) * 100 / 2
	return dur * (331.50 + 0.61 * temp) * 50

# 録音
def  record():
	p = pyaudio.PyAudio()

	stream = p.open(format=FORMAT,
					channels=CHANNELS,
					rate=RATE,
					input=True,
					frames_per_buffer=CHUNK)

	print("* recording")

	frames = []

	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
		data = stream.read(CHUNK)
		frames.append(data)

	print("* done recording")

	stream.stop_stream()
	stream.close()
	p.terminate()

	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()

	pass
# Mainを動かすコード
if __name__ == '__main__':
	setup()
	try:
		main()
	except KeyboardInterrupt:
		destroy()

