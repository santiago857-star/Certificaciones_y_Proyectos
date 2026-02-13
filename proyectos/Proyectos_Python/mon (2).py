import csv
import datetime
import json
import os
import itertools
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# Días de la semana
DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

def validar_dia(dia: str) -> str:
    """Verifica si el día ingresado es válido y lo devuelve con mayúscula inicial."""
    dia = dia.strip().lower()
    if dia.startswith("mie"):  # permite "mie", "miercoles", etc.
        return "Miércoles"
    for d in DIAS:
        if d.lower() == dia:
            return d
    raise ValueError(f"Día inválido: {dia}. Debe ser uno de: {', '.join(DIAS)}")

def leer_hora(hhmm: str) -> datetime.time:
    """Convierte un texto HH:MM a objeto hora."""
    try:
        return datetime.datetime.strptime(hhmm.strip(), "%H:%M").time()
    except ValueError:
        raise ValueError("Formato inválido. Usa HH:MM (24h), ej: 08:30")

# --- Entidades principales ---

@dataclass
class Alumno:
    id: int
    nombre: str
    apellido: str
    curso_id: Optional[int] = None

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

@dataclass
class Profesor:
    id: int
    nombre: str
    apellido: str

    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

@dataclass
class Curso:
    id: int
    nombre: str
    profesores: List[int] = field(default_factory=list)

@dataclass
class Horario:
    id: int
    curso_id: int
    profesor_id: int
    dia: str
    desde: datetime.time
    hasta: datetime.time

    def como_diccionario(self):
        return {
            "id": self.id,
            "curso_id": self.curso_id,
            "profesor_id": self.profesor_id,
            "dia": self.dia,
            "desde": self.desde.strftime("%H:%M"),
            "hasta": self.hasta.strftime("%H:%M")
        }

# --- Lógica principal del sistema ---

class SistemaEscolar:
    def __init__(self):
        self.alumnos: Dict[int, Alumno] = {}
        self.profesores: Dict[int, Profesor] = {}
        self.cursos: Dict[int, Curso] = {}
        self.horarios: Dict[int, Horario] = {}
        self._id_alumno = itertools.count(1)
        self._id_profesor = itertools.count(1)
        self._id_curso = itertools.count(1)
        self._id_horario = itertools.count(1)

    # ---- Crear entidades ----
    def crear_alumno(self, nombre: str, apellido: str) -> Alumno:
        aid = next(self._id_alumno)
        alumno = Alumno(aid, nombre.strip(), apellido.strip())
        self.alumnos[aid] = alumno
        return alumno

    def crear_profesor(self, nombre: str, apellido: str) -> Profesor:
        pid = next(self._id_profesor)
        profe = Profesor(pid, nombre.strip(), apellido.strip())
        self.profesores[pid] = profe
        return profe

    def crear_curso(self, nombre: str) -> Curso:
        cid = next(self._id_curso)
        curso = Curso(cid, nombre.strip())
        self.cursos[cid] = curso
        return curso

    # ---- Asignaciones ----
    def asignar_alumno_a_curso(self, alumno_id: int, curso_id: int):
        if alumno_id not in self.alumnos:
            raise ValueError("Alumno no encontrado")
        if curso_id not in self.cursos:
            raise ValueError("Curso no encontrado")
        self.alumnos[alumno_id].curso_id = curso_id

    def asignar_profesor_a_curso(self, profesor_id: int, curso_id: int):
        if profesor_id not in self.profesores:
            raise ValueError("Profesor no encontrado")
        if curso_id not in self.cursos:
            raise ValueError("Curso no encontrado")
        if profesor_id not in self.cursos[curso_id].profesores:
            self.cursos[curso_id].profesores.append(profesor_id)

    def crear_horario(self, curso_id: int, profesor_id: int, dia: str, desde: str, hasta: str) -> Horario:
        if curso_id not in self.cursos:
            raise ValueError("Curso no encontrado")
        if profesor_id not in self.profesores:
            raise ValueError("Profesor no encontrado")

        dia = validar_dia(dia)
        h_desde = leer_hora(desde)
        h_hasta = leer_hora(hasta)

        if h_desde >= h_hasta:
            raise ValueError("La hora de inicio debe ser menor a la de fin")

        # Verificar conflictos del profesor
        for h in self.horarios.values():
            if h.profesor_id == profesor_id and h.dia == dia:
                if not (h_hasta <= h.desde or h_desde >= h.hasta):
                    raise ValueError("Conflicto de horario para este profesor")

        hid = next(self._id_horario)
        horario = Horario(hid, curso_id, profesor_id, dia, h_desde, h_hasta)
        self.horarios[hid] = horario
        self.asignar_profesor_a_curso(profesor_id, curso_id)
        return horario

    # ---- Consultas ----
    def alumnos_de_curso(self, curso_id: int) -> List[Alumno]:
        return [a for a in self.alumnos.values() if a.curso_id == curso_id]

    def horario_de_profesor(self, profesor_id: int) -> List[Horario]:
        return sorted(
            [h for h in self.horarios.values() if h.profesor_id == profesor_id],
            key=lambda h: (DIAS.index(h.dia), h.desde)
        )

    def horario_de_curso(self, curso_id: int) -> List[Horario]:
        return sorted(
            [h for h in self.horarios.values() if h.curso_id == curso_id],
            key=lambda h: (DIAS.index(h.dia), h.desde)
        )

    # ---- Exportaciones ----
    def exportar_alumnos_csv(self, curso_id: int, archivo: str):
        curso = self.cursos[curso_id]
        alumnos = self.alumnos_de_curso(curso_id)
        with open(archivo, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["curso_id","curso","alumno_id","nombre","apellido"])
            writer.writeheader()
            for a in alumnos:
                writer.writerow({
                    "curso_id": curso.id,
                    "curso": curso.nombre,
                    "alumno_id": a.id,
                    "nombre": a.nombre,
                    "apellido": a.apellido
                })

    # (similar se haría para horario de profesor y curso...)

    # ---- Guardar y cargar ----
    def guardar(self, archivo: str):
        data = {
            "alumnos": [vars(a) for a in self.alumnos.values()],
            "profesores": [vars(p) for p in self.profesores.values()],
            "cursos": [vars(c) for c in self.cursos.values()],
            "horarios": [h.como_diccionario() for h in self.horarios.values()]
        }
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def cargar(self, archivo: str):
        if not os.path.exists(archivo):
            raise FileNotFoundError(archivo)
        with open(archivo, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.__init__()
        for a in data["alumnos"]:
            self.alumnos[a["id"]] = Alumno(**a)
        for p in data["profesores"]:
            self.profesores[p["id"]] = Profesor(**p)
        for c in data["cursos"]:
            self.cursos[c["id"]] = Curso(**c)
        for h in data["horarios"]:
            self.horarios[h["id"]] = Horario(
                id=h["id"],
                curso_id=h["curso_id"],
                profesor_id=h["profesor_id"],
                dia=h["dia"],
                desde=leer_hora(h["desde"]),
                hasta=leer_hora(h["hasta"])
            )

# --- Menú en consola ---
def menu():
    sistema = SistemaEscolar()
    print("📚 Bienvenido al Sistema Escolar 📚")

    while True:
        print("\n--- Menú ---")
        print("1) Crear alumno")
        print("2) Crear profesor")
        print("3) Crear curso")
        print("4) Asignar alumno a curso")
        print("5) Asignar profesor a curso")
        print("6) Crear horario")
        print("7) Exportar alumnos de un curso (CSV)")
        print("0) Salir")

        opcion = input("Elige una opción: ").strip()
        try:
            if opcion == "1":
                n = input("Nombre: "); a = input("Apellido: ")
                al = sistema.crear_alumno(n, a)
                print(f"Alumno creado: {al.id} {al.nombre_completo()}")
            elif opcion == "2":
                n = input("Nombre: "); a = input("Apellido: ")
                pr = sistema.crear_profesor(n, a)
                print(f"Profesor creado: {pr.id} {pr.nombre_completo()}")
            elif opcion == "3":
                nombre = input("Nombre del curso: ")
                c = sistema.crear_curso(nombre)
                print(f"Curso creado: {c.id} {c.nombre}")
            elif opcion == "4":
                aid = int(input("ID alumno: ")); cid = int(input("ID curso: "))
                sistema.asignar_alumno_a_curso(aid, cid)
                print("✅ Alumno asignado al curso")
            elif opcion == "5":
                pid = int(input("ID profesor: ")); cid = int(input("ID curso: "))
                sistema.asignar_profesor_a_curso(pid, cid)
                print("✅ Profesor asignado al curso")
            elif opcion == "6":
                pid = int(input("ID profesor: "))
                cid = int(input("ID curso: "))
                d = input("Día: ")
                desde = input("Hora inicio (HH:MM): ")
                hasta = input("Hora fin (HH:MM): ")
                h = sistema.crear_horario(cid, pid, d, desde, hasta)
                print(f"Horario creado ID={h.id}")
            elif opcion == "7":
                cid = int(input("ID curso: "))
                archivo = input("Archivo destino CSV: ")
                sistema.exportar_alumnos_csv(cid, archivo)
                print("✅ Exportación lista")
            elif opcion == "0":
                print("👋 Adiós!")
                break
        except Exception as e:
            print("⚠️ Error:", e)

if __name__ == "__main__":
    menu()
