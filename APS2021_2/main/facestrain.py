import os
from PIL import Image
import numpy as np
import cv2
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
img_dir = os.path.join(BASE_DIR,"images")

faces_cascade = cv2.CascadeClassifier('main\cascades\data\haarcascade_frontalface_alt2.xml')

recognizer = cv2.face.LBPHFaceRecognizer_create()

class FaceTrain(object):
	def __init__(self):
		current_id = 0
		label_ids = {}
		y_labels = []  # tem os valores das labels
		x_train = []  # tem os números dos valores de pixel

		for root, dirs, files in os.walk(img_dir):
			for file in files:
				if file.endswith("png") or file.endswith("jpg"):#ver se os valores são png ou jpg
					path = os.path.join(root,file)
					label = os.path.basename(root).replace(" ", "-").lower()

					if not label in label_ids:
						label_ids[label] = current_id
						current_id += 1

					id_ = label_ids[label]

					pil_image = Image.open(path).resize((550,550),Image.ANTIALIAS)#abre cada imagem e faz um resize nelas

					image_array = np.array(pil_image,"uint8")#converte a imagem em matrizes


					faces = faces_cascade.detectMultiScale(image_array, minNeighbors=5)

					for (x,y,w,h) in faces:
						roi = image_array[y:y+h,x:x+w]
						x_train.append(roi)
						y_labels.append(id_)

		with open("labels.pickle","wb") as f:#writing bytes
			pickle.dump(label_ids, f)

		recognizer.train(x_train, np.array(y_labels))
		recognizer.save("trainner.yml")