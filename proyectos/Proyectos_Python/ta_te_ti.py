def imprimir_tablero(tablero):
    for fila in tablero:
        print("|" + "|".join(fila) + "|")
    print()

def hay_ganador(tablero, simbolo):
    for i in range(3):
        if all(tablero[i][j] == simbolo for j in range(3)) or all(tablero[j][i] == simbolo for j in range(3)):
            return True
    return tablero[0][0] == tablero[1][1] == tablero[2][2] == simbolo or tablero[0][2] == tablero[1][1] == tablero[2][0] == simbolo

def empate(tablero):
    return all(celda != "_" for fila in tablero for celda in fila)

def jugar():
    tablero = [["_"] * 3 for _ in range(3)]
    turno = "X"
    
    while True:
        imprimir_tablero(tablero)
        
        try:
            fila, columna = map(int, input(f"Jugador {turno}, elige fila y columna (0-2): ").split())
            if not (0 <= fila < 3 and 0 <= columna < 3 and tablero[fila][columna] == "_"):
                print("Posición inválida intenta de nuevo.")
                continue
            tablero[fila][columna] = turno
        except (ValueError, IndexError):
            print("Entrada inválida ingresa dos números entre 0 y 2.")
            continue
        
        if hay_ganador(tablero, turno):
            imprimir_tablero(tablero)
            print(f"El jugador {turno} ha ganado")
            break
        if empate(tablero):
            imprimir_tablero(tablero)
            print("Es un empate")
            break
        
        turno = "O" if turno == "X" else "X"

if __name__ == "__main__":
    jugar()
