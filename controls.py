""" This script detects a object of specified object colour from the webcam video feed.
Using OpenCV library for vision tasks and HSV color space for detecting object of given specific color."""

# --------------------------------------------------------------------------
# ------- PLANTILLA DE CÓDIGO ----------------------------------------------
# ------- Coceptos básicos de PDI-------------------------------------------
# ------- Por: Daniel Santa Rendón --------------
# ------- Por: Bryan Zuleta Veléz --------------
# -------      PFacultad de Ingenieria   -----------------
# ------- Curso Básico de Procesamiento de Imágenes y Visión Artificial-----
# ------- Abril 2021--------------------------------------------------
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# --1. Importación de modulos necesarios en el sistema ---------------------
# --------------------------------------------------------------------------

import os

os.environ["DISPLAY"] = ":0"
os.environ["XAUTHORITY"] = "/run/user/1000/gdm/Xauthority"

import cv2
import imutils
import pyautogui
from collections import deque
import time


class Controls:

    # --------------------------------------------------------------------------
    # -- 2. Inicialización de variables, carga de imágenes  --------------------
    # --------------------------------------------------------------------------
    def main(self):
        # Definr color HSV del rango de color de objetos verdes
        self.greenLower = (50, 40, 200)
        self.greenUpper = (86, 255, 255)
        self.backgorung = self.load_image("./imgs/controls_background.png")
        # Usar en una estructura cola para almancenar los puntos en buffer
        self.buffer = 20

        self.pts = deque(maxlen=self.buffer)

        # Inicia video
        self.video_capture = cv2.VideoCapture(0)
        time.sleep(2)

        # Start video capture
        self.video_camera()

    """
    Funcion con un ciclo para guardar la captura de la camara infinito
    """

    def video_camera(self):

        while True:
            # ---- Almancenar el frame leido -----------------------------------------------
            _, frame = self.video_capture.read()
            # Dar la vuelta del frame para evitar el efecto de espejo ---------------------
            frame = cv2.flip(frame, 1)
            # ---- Cambio de ventana tamaño a 600x600 --------------------------------------
            frame = imutils.resize(frame, width=500)

            # ---- Llamado de la función para aplicar las técnicas -------------------------
            hsv_converted_frame = self.filter_techniques(frame)

            # ---- Crear máscara para el frame, mostrando valores verdes -------------------
            mask = cv2.inRange(hsv_converted_frame, self.greenLower, self.greenUpper)
            # ---- Erosionar la salida para eliminar los pequeños puntos blancos presentes en la imagen enmascarada
            mask = cv2.erode(mask, None, iterations=2)
            # ---- Dilatar la imagen resultante para guardar como nuestro nuevo objetivo ---
            mask = cv2.dilate(mask, None, iterations=2)

            # ---- Display the masked output in a different window --------------------------
            cv2.imshow("Masked Output", mask)

            # ----  Encuentra todos los contornos en la imagen con la máscara --------------------
            cnts, _ = cv2.findContours(
                mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            # ----  Definir el centro de la imagen -----------------------------------------------
            center = None

            # ----  Si hay algún objeto detectado, entonces procede ------------------------------
            if (len(cnts)) > 0:
                # ----  Encuentra el contorno con la máxima área ---------------------------------
                c = max(cnts, key=cv2.contourArea)
                # ----  Encuentra el centro del circulo y su radio de la detección mas grande del contorno
                ((x, y), radius) = cv2.minEnclosingCircle(c)

                # ----  Calcular el centroide del área -------------------------------------------
                center = self.centroid_calculate(c)

                if x > 320 and y > 74 and y < 207:
                    pyautogui.press("right", _pause=False)
                elif x < 170 and y > 35 and y < 200:
                    pyautogui.press("left", _pause=False)
                elif y < 74 and x > 150 and x < 350:
                    pyautogui.press("up", _pause=False)
                elif y > 207 and x > 150 and x < 350:
                    pyautogui.press("down", _pause=False)

                # ----  Procede sólo si el tamaño del circulo es grande -------------------------
                if radius > 10:
                    radius = 30
                    # ----  Dibujar los circulos alrededor del objeto ---------------------------
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 255, 255), -1)

                # ----  Concatena los centroides detectados -------------------------------------
                self.pts.appendleft(center)

            # ----  Mostrar el frame con la detección -------------------------------------------
            alpha = 0.5
            added_image = cv2.addWeighted(
                frame[0:281, 0:500, :],
                alpha,
                self.backgorung[0:281, 0:500, :],
                1 - alpha,
                0,
            )
            frame[0:281, 0:500] = added_image

            cv2.imshow("Frame", frame)
            key = cv2.waitKey(1) & 0xFF

            # ----  Si q se sale de la ventana --------------------------------------------------
            if key == ord("q"):
                self.quit()

    # --------------------------------------------------------------------------
    # -- 3. Cálculo del centroide  --------------------
    # --------------------------------------------------------------------------
    def centroid_calculate(self, c):
        # ----  Calcular el centroide alrededor del objeto para dibujarlo -----------------------
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        return center

    # --------------------------------------------------------------------------
    # -- 4. Tecnicas de filtrado sobre las imágenes  ---------------------------
    # --------------------------------------------------------------------------
    def filter_techniques(self, frame):
        # ----  Aplicar filtro gaussian bllur de tamaño 5, remover el exceso de ruido -----------
        blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)
        # ----  Convertir frame rgb a hsv para mejor segmentacion -------------------------------
        hsv_converted_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
        return hsv_converted_frame
    
    def load_image(self, image_url):
        image = cv2.imread(image_url)
        return cv2.resize(image, (500, 281))

    def quit(self):
        self.video_capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    controls = Controls()
    controls.main()
