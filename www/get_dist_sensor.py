#!/usr/bin/env python
# -*- coding: utf-8 -*-

from RPi import GPIO

PORT = 8

def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PORT, GPIO.IN)
    try:
        value = GPIO.input(PORT)
        print value
    except Exception as e:
        print e
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
