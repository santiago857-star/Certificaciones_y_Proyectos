import random

def tirar_dados():
    dado1 = random.randint(1, 6)
    dado2 = random.randint(1, 6)
    suma = dado1 + dado2
    print( "dado1:" , dado1)
    print("Dado2:", dado2)
    print("Suma:", suma)

def main():
    print("Hala,Bienvenido al simulador de dados")
    while True:
        tirar_dados()
        repetir = input("\n¿Quieres tirar los dados otra vez? (s/n): ").lower()
        if repetir != 's':
            print("¡Gracias por jugar! ")
            break

if __name__ == "__main__":
    main()
