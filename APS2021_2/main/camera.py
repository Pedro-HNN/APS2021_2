import cv2
import os
import pickle
from main.models import Person
from main.facestrain import FaceTrain
import operator

face_cascade = cv2.CascadeClassifier('main\cascades\data\haarcascade_frontalface_alt2.xml')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
img_dir = os.path.join(BASE_DIR,"images")
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trainner.yml")

#cria as labels para a IA identificar os rostos
def createLabels():
    labels = {}
    with open("labels.pickle", "rb") as f:  # load bytes
        labels1 = pickle.load(f)
        labels = {v: k for k, v in labels1.items()}

    return labels

#checa para ver se tem alguém registrado na database
def theresFace():
    if Person.objects.count() != 0:
        return True
    else:
        return False

class RegistrationCamera(object):

    def __init__(self,response):

        self.name = response.POST.get('name', None)
        self.email = response.POST.get('email', None)
        self.level = response.POST.get('level', None)
        self.faces = {}
        self.video = cv2.VideoCapture(0)

        # checa se o email está na database
        try:
            obj = Person.objects.get(email=self.email)
            self.validEmail = False
        except:
            self.validEmail = True

        self.update()

    def update(self):

        if self.validEmail:
            j = 1  # index dos nomes das imagens
            limit = 50  # limite das imagens
            running = True #variável para a parada
            facerec = 0 #index para timing de reconhecimento facial

            self.validFace = False
            theresface = theresFace()

            while running:
                self.grabbed, self.frame = self.video.read()
                gray = cv2.cvtColor(self.frame,cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray)

                for (x, y, w, h) in faces:#ao reconhecer a face
                    roi_gray = gray[y:y + h, x:x + w] #tira uma imagem só da face em preto e branco

                    #desenha retângulo
                    width = x + w
                    height = y + h
                    cv2.rectangle(self.frame, (x, y), (width, height), (255, 0, 0), 2)
                    #desenha retângulo

                    if theresface:
                        #reconhecimento facial
                        if facerec <= limit:
                            id_, conf = recognizer.predict(roi_gray)
                            labels = createLabels()
                            facerec += 1
                            if 40 <= conf <= 80:
                                if labels[id_] in self.faces:#se reconhecerem a imagem, o id vai pro dicionário
                                    self.faces[labels[id_]] += 1
                                else:
                                    self.faces[labels[id_]] = 1
                            else:
                                if "valid" in self.faces:#se não reconhecerem a imagem, a palavra "valid" é colocada no dicionário
                                    self.faces["valid"] += 1
                                else:
                                    self.faces["valid"] = 1
                        #reconhecimento facial
                        #contagem após o reconhecimento
                        else:
                            maxface = max(self.faces.items(), key=operator.itemgetter(1))[0]
                            if maxface == "valid":#se tiver mais valid do que qualquer outro id, é porque o rosto é válido
                                self.validFace = True
                            else:
                                self.validFace = False
                                running = False
                        # contagem após o reconhecimento
                    else:#caso não tenha ninguém registrado no DB
                        self.validFace = True

                    #cadastrando imagens na face
                    if self.validFace:
                        if j == 1:
                            self.path = os.path.join(img_dir, self.email)
                            os.mkdir(self.path)#criando pasta com o email
                            p = Person(name=self.name, email=self.email, level=self.level)
                            p.save()#salvando dados no DB

                            self.level = p.get_level()#pega o valor do level
                        if j <= limit:
                            cv2.imwrite(f"{self.path}/{j}.png", roi_gray)#salvando imagens na pasta
                            j += 1
                        else:
                            running = False#depois de acabar de salvar tudo, fechar o programa
                    #cadastrando imagem na face

                cv2.imshow('Webcam', self.frame)

                #caso a pessoa apertar Q, o programa fecha
                if cv2.waitKey(20) & 0xFF == ord('q'):
                    self.video.release()
                    cv2.destroyAllWindows()
                #caso a pessoa apertar Q, o programa fecha

            FaceTrain() #roda o treino da IA
            self.video.release()
            cv2.destroyAllWindows()

    def getValidEmail(self):
        return self.validEmail

    def getValidFace(self):
        return self.validFace

    def getValues(self):
        values = [self.name,self.email,self.level]
        return values

class LoginCamera(object):

    def __init__(self):
        self.faces = {}
        self.video = cv2.VideoCapture(0)
        self.update()

    def update(self):
        limit = 50 #limite de checks
        facerec = 0 #index para timing de reconhecimento facial
        running = True #variável para a parada

        self.theresFace = theresFace()

        if self.theresFace:
            FaceTrain() #roda o treino da IA
            while running:
                self.grabbed, self.frame = self.video.read()

                gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray)

                for (x, y, w, h) in faces:#ao reconhecer a face
                    roi_gray = gray[y:y + h, x:x + w] #tira uma imagem só da face em preto e branco

                    # desenha retângulo
                    width = x + w
                    height = y + h
                    cv2.rectangle(self.frame, (x, y), (width, height), (255, 0, 0), 2)
                    # desenha retângulo

                    #reconhecimento facial
                    id_, conf = recognizer.predict(roi_gray) #peg
                    labels = createLabels()
                    if 40 <= conf <= 80:
                        if labels[id_] in self.faces:#se encontrarem um id, o id é adicionado no dicionário
                            self.faces[labels[id_]] += 1
                        else:
                            self.faces[labels[id_]] = 1
                    else:
                        if "invalid" in self.faces:#se não achar nenhuma face, então a palavra invalid é adicionada no dicionário
                            self.faces["invalid"] += 1
                        else:
                            self.faces["invalid"] = 1
                    facerec += 1
                    #reconhecimento facial

                    if facerec >= limit:
                        running = False #depois do check, fecha o programa
                    self.theresFace = True

                cv2.imshow('Webcam', self.frame)

                # tirar depois
                if cv2.waitKey(20) & 0xFF == ord('q'):
                    self.video.release()
                    cv2.destroyAllWindows()


            self.email = max(self.faces.items(), key=operator.itemgetter(1))[0]
            if self.email == "invalid":#se o id der "invalid", quer dizer que a IA não reconheceu esse rosto
                self.valid = False
            else:
                obj = Person.objects.get(email=self.email)
                self.name = getattr(obj, "name")
                self.level = obj.get_level()#pega o valor do level

                self.valid = True

            self.video.release()
            cv2.destroyAllWindows()

    def getValid(self):
        return self.valid

    def getTheresFace(self):
        return self.theresFace

    def getValues(self):
        values = [self.name,self.email,self.level]
        return values