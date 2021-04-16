# --------------------------------------------------------------------------
# ------- PLANTILLA DE CÓDIGO ----------------------------------------------
# ------- Conceptos básicos de PDI------------------------------------------
# ------- Por: Daniel Santa Rendón   daniel.santar@udea.edu.co--------------
# -------      Estudiante de ingeniería de sistemas ------------------------
# -------      Universidad de Antioquia ------------------------------------
# ------- Por: Bryan Zuleta Veléz    bryan.zuleta@udea.edu.co---------------
# -------      Estudiante de ingeniería de sistemas ------------------------
# -------      Universidad de Antioquia ------------------------------------
# ------- Curso Básico de Procesamiento de Imágenes y Visión Artificial-----
# ------- Abril 2021--------------------------------------------------
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# --1. Importación de modulos necesarios en el sistema ---------------------
# --------------------------------------------------------------------------


# Asignación de variables de ambiente requeridas para el uso de la pantalla y de la cámara
import os

# Esta variable de entorno indica al sistema cual "pantalla" debe ejecutarse
# El valor :0.0 significa host local, primer controlador gráfico y primera pantalla física conectada
os.environ["DISPLAY"] = ":0.0"
# Esta variable de entorno es el nombre del archivo para los permisos requeridos para conectar al servidor
os.environ["XAUTHORITY"] = "/run/user/1000/gdm/Xauthority"


from collections import (
    deque,
)  # Abreviatura para double-ended queue o cola doblemente terminada

import cv2  # Opencv para python
import imutils  # Libreria para funciones básicas sobre imágenes
import pyautogui  # Permite a python controlar teclado y mouse


class Controls:

    # --------------------------------------------------------------------------------------------------------------
    # -- 2. Inicialización de las variables de la clase y carga de la imagen de fondo de los controles -------------
    # --------------------------------------------------------------------------------------------------------------
    def main(self):
        # ---- Límites inferiores en el mapa HSV -------------------------------------------------------------------
        self.greenLower = (50, 40, 200)
        # ---- Superiores inferiores en el mapa HSV ----------------------------------------------------------------
        self.greenUpper = (86, 255, 255)
        # ---- Carga de la imagen png para el fondo de los controles -----------------------------------------------
        self.backgorung = self.load_image("./imgs/controls_background.png")

        # ---- Máxima longitud del deque ---------------------------------------------------------------------------
        self.buffer = 20
        # ---- Se crea un nuevo objeto deque -----------------------------------------------------------------------
        self.pts = deque(maxlen=self.buffer)

        # ---- Inicia video ----------------------------------------------------------------------------------------
        self.video_capture = cv2.VideoCapture(0)

        # ---- Inicio del loop para el procesamiento de imagen -----------------------------------------------------
        self.video_camera()

    def video_camera(self):
        while True:
            # ---- Almancenar el frame leido -----------------------------------------------------------------------
            _, frame = self.video_capture.read()
            # ---- Dar la vuelta del frame para evitar el efecto de espejo -----------------------------------------
            frame = cv2.flip(frame, 1)
            # ---- Re dimensiona el frame a un ancho de 500 pixeles ------------------------------------------------
            frame = imutils.resize(frame, width=500)

            # ---- Llamado de la función para aplicar las técnicas -------------------------------------------------
            hsv_converted_frame = self.filter_techniques(frame)

            # ---- Crear máscara para el frame detectando valores verdes -------------------------------------------
            mask = cv2.inRange(hsv_converted_frame, self.greenLower, self.greenUpper)
            # ---- Erosionar y dilata la salida para eliminar los pequeños puntos blancos en la imagen enmascarada -
            mask = cv2.erode(mask, None, iterations=2)
            mask = cv2.dilate(mask, None, iterations=2)

            # ---- Muestra la pantalla de la máscara en otra ventana -----------------------------------------------
            cv2.imshow("Masked Output", mask)

            # ---- Encuentra todos los contornos en la imagen con la máscara ---------------------------------------
            cnts, _ = cv2.findContours(
                mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            # ---- Si detecta algún ejemplo cumple la condición ----------------------------------------------------
            if (len(cnts)) > 0:
                # ---- Encuentra el contorno con la máxima área ----------------------------------------------------
                c = max(cnts, key=cv2.contourArea)
                # ---- Encuentra el centro del circulo y su radio de la detección mas grande del contorno ----------
                ((x, y), radius) = cv2.minEnclosingCircle(c)

                # ----  Calcular el centroide del área -------------------------------------------------------------
                center = self.centroid_calculate(c)

                # ---- Posiciones en la pantalla para presionar botones --------------------------------------------
                if x > 300 and y > 74 and y < 207:
                    pyautogui.press("right", _pause=False)
                elif x < 170 and y > 35 and y < 200:
                    pyautogui.press("left", _pause=False)
                elif y < 90 and x > 150 and x < 350:
                    pyautogui.press("up", _pause=False)
                elif y > 180 and x > 150 and x < 350:
                    pyautogui.press("down", _pause=False)

                # ----  Cumple la si el radio del objeto detectado es mayor a 10 ------------------------------------
                if radius > 5:
                    # ----  Dibujar los circulos alrededor del objeto -----------------------------------------------
                    cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                    cv2.circle(frame, center, 5, (0, 255, 255), -1)

                # ----  Concatena los centroides detectados ---------------------------------------------------------
                self.pts.appendleft(center)

            # ----  Se suma la imagen de los controles con la de la cámara  -----------------------------------------
            alpha = 0.5
            frame = cv2.addWeighted(
                frame[0:281, 0:500, :],
                alpha,
                self.backgorung[0:281, 0:500, :],
                1 - alpha,
                0,
            )

            # ---- Se muestra en pantalla el frame resultante -------------------------------------------------------
            cv2.imshow("Frame", frame)

            # ----  Si q se sale de la ventana ----------------------------------------------------------------------
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                self.quit()

    # ---------------------------------------------------------------------------------------------------------------
    # ---- 3. Cálculo del centroide  --------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------------------------
    def centroid_calculate(self, c):
        # ----  Calcular el centroide alrededor del objeto para dibujarlo -------------------------------------------
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
        return center

    # ---------------------------------------------------------------------------------------------------------------
    # ---- 4. Tecnicas de filtrado sobre las imágenes  --------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------------------------
    def filter_techniques(self, frame):
        # ----  Aplicar filtro gaussian blur de tamaño 5, remover el exceso de ruido -------------------------------
        blurred_frame = cv2.GaussianBlur(frame, (5, 5), 0)
        # ----  Convertir frame rgb a hsv para mejor segmentacion ---------------------------------------------------
        hsv_converted_frame = cv2.cvtColor(blurred_frame, cv2.COLOR_BGR2HSV)
        return hsv_converted_frame

    # ---- Método para cargar y redimensionar la imagen del background de los controles -----------------------------
    def load_image(self, image_url):
        image = cv2.imread(image_url)
        return cv2.resize(image, (500, 281))

    # ---- Método para cerrar las ventanas --------------------------------------------------------------------------
    def quit(self):
        self.video_capture.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    controls = Controls()
    controls.main()
