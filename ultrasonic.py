import RPi.GPIO as GPIO
import time


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


def init_sensors(trig, echo, mode=GPIO.BCM):
    """
    初期化します
    :param trig: Trigger用ピン番号、またはGPIO 番号
    :param echo: Echo用ピン番号、またはGPIO 番号
    :param mode: GPIO.BCM、または GPIO.BOARD (default:GPIO.BCM)
    :return: なし
    """
    GPIO.cleanup()
    GPIO.setmode(mode)
    GPIO.setup(trig, GPIO.OUT)
    GPIO.setup(echo, GPIO.IN)


def get_distance(trig, echo, temp=15):
    """
    距離を取得します。取得に失敗した場合は0を返します。
    :param trig: Trigger用ピン番号、またはGPIO 番号(GPIO.setmodeに依存。)(GPIO.OUT)
    :param echo: Echo用ピン番号、またはGPIO 番号(GPIO.setmodeに依存。)(GPIO.IN)
    :param temp: 取得可能であれば温度(default:15℃)
    :return: 距離（ｃｍ）タイムアウト時は 0
    """

    # 出力を初期化
    GPIO.output(trig, GPIO.LOW)
    time.sleep(0.3)
    # 出力(10us以上待つ)
    GPIO.output(trig, GPIO.HIGH)
    time.sleep(0.000011)
    # 出力停止
    GPIO.output(trig, GPIO.LOW)

    # echo からパルスを取得
    dur = pulse_in(echo, GPIO.HIGH, 1.0)

    # ( パルス時間 x 331.50 + 0.61 * 温度 ) x (単位をcmに変換) x 往復
    # return dur * (331.50 + 0.61 * temp) * 100 / 2
    return dur * (331.50 + 0.61 * temp) * 50


if __name__ == "__main__":

    GPIO_TRIG = 26
    GPIO_ECHO = 19

    init_sensors(GPIO_TRIG, GPIO_ECHO)
    while True:
        print("距離：{0} cm".format(get_distance(GPIO_TRIG, GPIO_ECHO)))
        time.sleep(2)