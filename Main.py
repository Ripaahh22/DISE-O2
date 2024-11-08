import time
import serial
import RPi.GPIO as GPIO
import subprocess

# Configura la conexión serial con el Arduino
ser = serial.Serial('/dev/ttyACM0', 9600)

# Configuración de los pines de los botones en la Raspberry Pi
BUTTON_PINS = [17, 22, 27, 13, 5, 19, 6]
GPIO.setmode(GPIO.BCM)
for pin in BUTTON_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

game_started = False
music_process = None
failed_attempts = 0  # Contador de intentos fallidos
max_attempts = 5     # Número máximo de intentos permitidos

def send_command(command):
    ser.write((command + '\n').encode())
    print(f"Comando enviado a Arduino: {command}")  # Mensaje de depuración

try:
    while True:
        if not game_started:
            # Reinicia el contador de intentos fallidos
            failed_attempts = 0
            # Espera el comando para iniciar el juego con la dificultad elegida
            for pin in BUTTON_PINS:
                if GPIO.input(pin) == GPIO.LOW:
                    # Detecta cuál botón fue presionado
                    if pin == 22:  # Amarillo - Fácil
                        print("Botón Amarillo presionado: Iniciando en dificultad Fácil")
                        send_command("START_GAME_EASY")
                    elif pin == 17:  # Azul - Medio
                        print("Botón Azul presionado: Iniciando en dificultad Media")
                        send_command("START_GAME_MEDIUM")
                    elif pin == 5:  # Blanco - Difícil
                        print("Botón Blanco presionado: Iniciando en dificultad Difícil")
                        send_command("START_GAME_HARD")
                    else:
                        print(f"Botón desconocido en pin {pin}")

                    # Inicia la música y el juego
                    music_process = subprocess.Popen(["aplay", "cancion.wav"])
                    game_started = True
                    time.sleep(0.5)
                    break
        else:
            # Lógica del juego en curso
            for index, pin in enumerate(BUTTON_PINS):
                if GPIO.input(pin) == GPIO.LOW:
                    command = f"CHECK_STRIP_{index + 1}"
                    send_command(command)
                    print(f"Comando enviado: {command}")

                    # Espera a que se suelte el botón antes de continuar
                    while GPIO.input(pin) == GPIO.LOW:
                        time.sleep(0.1)
            time.sleep(0.1)

except KeyboardInterrupt:
    print("Cerrando el juego y limpiando los pines GPIO...")
    send_command("END_GAME")  # Finaliza el juego en Arduino si se interrumpe
    if music_process:
        music_process.terminate()
    ser.close()
    GPIO.cleanup()
