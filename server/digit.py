import os
import cv2
import numpy as np
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
from keras.models import load_model

model = load_model('weight/mnist.h5')


def digit_recog(img):
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	h, w = img.shape
	width_per_num = w/8
	result = ''
	for k in range(8):
	  # start = int(width_per_num*k)+1
	  # end = int(width_per_num*(k+1))
		start = int(width_per_num*k)
		end = int(width_per_num*(k+1))
		digit = cv2.resize(img[:, start:end], [28, 28])
		# digit = cv2.threshold(digit, 185, 255, cv2.THRESH_BINARY_INV)[1]
		digit = cv2.adaptiveThreshold(digit,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,27,2)
		digit[0:4, :] = np.zeros([4, 28])
		digit[24:28, :] = np.zeros([4, 28])
		digit[:, 0:4] = np.zeros([28, 4])
		digit[:, 24:28] = np.zeros([28, 4])
		temp = np.argmax((model.predict(np.expand_dims(digit, axis=0), verbose=0)))
		result += str(temp)

	return result