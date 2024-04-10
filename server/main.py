from flask import Flask, request, jsonify
from flask_cors import CORS
from byteImage import readb64, imgToBase64, auto_scoring
import matplotlib.pyplot as plt
import cv2
import base64

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["POST"])
def home():
	base64_img = request.get_json(force=True)['image']
	img = readb64(base64_img)

	scored_img = auto_scoring(img)

	if scored_img.any():
		print("Tot")
		# scored_img = cv2.resize(scored_img, (700, 700))  
		# cv2.imshow("hghg", scored_img)
		# cv2.waitKey()

		base64_scored_img = imgToBase64(scored_img)

		response = jsonify({"status_ne": True, "anh_dc_cham": base64_scored_img})
		response.headers.add("Access-Control-Allow-Origin", "*")
		return response

	else:
		print("Loi")
		response = jsonify({"status_ne": False, "anh_dc_cham": ""})
		response.headers.add("Access-Control-Allow-Origin", "*")
		return response
	

if __name__ == "__main__":
	app.run()