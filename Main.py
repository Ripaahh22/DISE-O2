import time
import serial
import RPi.GPIO as GPIO
import subprocess

# Configura la conexión serial con el Arduino
ser = serial.Serial('/dev/ttyACM0', 9600)

# Configuración de los pines de los botones en la Raspberry Pi
BUTTON_PINS = {
    17: "START_GAME_MEDIUM",  # Azul - Dificultad Media
    22: "START_GAME_EASY",    # Amarillo - Dificultad Fácil
    5: "START_GAME_HARD"      # Blanco - Dificultad Difícil
}

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
            # Espera a que un botón de dificultad sea presionado para iniciar el juego
            for pin, command in BUTTON_PINS.items():
                if GPIO.input(pin) == GPIO.LOW:
                    print(f"Botón en GPIO {pin} presionado: Enviando {command}")
                    send_command(command)  # Envía el comando de inicio de dificultad

                    # Inicia la música y el juego
                    music_process = subprocess.Popen(["aplay", "cancion.wav"])
                    game_started = True
                    time.sleep(0.5)  # Evita múltiples envíos rápidos
                    break
        else:
            # Lógica del juego en curso para verificar pulsaciones de botones
            for pin in BUTTON_PINS:
                if GPIO.input(pin) == GPIO.LOW:
                    index = BUTTON_PINS.keys().index(pin) + 1
                    command = f"CHECK_STRIP_{index}"
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
