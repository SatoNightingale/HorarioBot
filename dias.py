from datetime import date
import sqlite3
from sql_utils import get_db_entry


nombre_turnos = {
    1: "1️⃣ <i>Primera</i>",
    2: "2️⃣ <i>Segunda</i>",
    3: "3️⃣ <i>Tercera</i>"
}

meses = {
    1: 'enero',
    2: 'febrero',
    3: 'marzo',
    4: 'abril',
    5: 'mayo',
    6: 'junio',
    7: 'julio',
    8: 'agosto',
    9: 'septiembre',
    10: 'octubre',
    11: 'noviembre',
    12: 'diciembre'
}

dias_semana = {
    0: 'lunes',
    1: 'martes',
    2: 'miércoles',
    3: 'jueves',
    4: 'viernes',
    5: 'sábado',
    6: 'domingo'
}


class Turno:
    def __init__(self, fecha, num, /, id_asig=None, modif=None, otro=None):
        self.fecha = fecha
        self.num = num

        self.id_asignatura = id_asig
        self.asignatura = None
        self.modificador = None
        self.es_cp = modif == '0'
        self.otro = None

        con = sqlite3.connect("datos.db")

        if id_asig and id_asig != 'NULL' and id_asig != 0:
            self.asignatura = get_db_entry('Asignatura', ['Nombre'], id_asig, con)[0]
            if modif != 'NULL':
                self.modificador = get_db_entry('Modificador_Turno', ['descripcion'], modif, con, prim_key_name='simbolo', as_string=True)[0]
        elif otro != 'NULL':
            self.otro = get_db_entry('Otros', ['descripcion'], otro, con, prim_key_name='simbolo', as_string=True)[0]

        con.close()

    def __str__(self):
        turno_texto = 'Libre'

        if self.asignatura:
            turno_texto = self.asignatura
            if self.modificador:
                turno_texto = f"{self.asignatura} ({self.modificador})"
            if not self.es_cp:
                profesor = self.profesor_principal()
                turno_texto += f"\n  <i>Profesor</i>: {profesor}"
            else:
                profesores = self.profesores_clase_practica()
                if len(profesores) > 0:
                    profes_text = '\n'.join([f'  • {p}' for p in profesores])
                    turno_texto += f"\n  <i>Profesor de clase práctica</i>:\n{profes_text}"
        elif self.otro:
            turno_texto = self.otro
        
        return turno_texto

    def esLibre(self):
        return not self.asignatura and not self.otro
    
    def profesor_principal(self):
        con = sqlite3.connect("datos.db")
        cur = con.cursor()
        query = f"""SELECT Profesor.Nombre
            FROM Asignatura, Profesor
            WHERE Asignatura.id_prof_princ = Profesor.id
            AND Asignatura.id = {self.id_asignatura}"""
        query_result = cur.execute(query)
        nombre_prof = query_result.fetchone()[0]
        con.close()
        return nombre_prof
    
    def profesores_clase_practica(self):
        con = sqlite3.connect("datos.db")
        cur = con.cursor()
        query = f"""SELECT Profesor.Nombre
            FROM Asignatura, imparte_clase_practica, Profesor
            WHERE Asignatura.id = imparte_clase_practica.id_asig
            AND Profesor.id = imparte_clase_practica.id_prof
            AND Asignatura.id = {self.id_asignatura}"""
        query_result = cur.execute(query)
        query_profes = query_result.fetchall()
        list_profes = [str(x[0]) for x in query_profes]
        con.close()
        return list_profes



class Dia:
    def __init__(self, fecha: date, turnos = list[Turno]):
        self.fecha = fecha
        self.turnos = turnos
    
    def __str__(self):
        fecha = f"{dias_semana[self.fecha.weekday()].capitalize()}, {self.fecha.day} de {meses[self.fecha.month]} de {self.fecha.year}"
        
        manana = ['<strong><u>🌅 Mañana</u></strong>']
        manana_libre = True
        for i, turno in enumerate(self.turnos[0:3]):
            manana.append(f"{nombre_turnos[i+1]}: {turno}")
            if not turno.esLibre():
                manana_libre = False
        
        tarde = ['<strong><u>🌄 Tarde</u></strong>']
        tarde_libre = True
        for i, turno in enumerate(self.turnos[3:6]):
            tarde.append(f"{nombre_turnos[i+1]}: {turno}")
            if not turno.esLibre():
                tarde_libre = False
        
        if manana_libre: manana = ['Mañana', '👋 Libre']
        if tarde_libre: tarde = ['Tarde', '👋 Libre']

        ret = '\n'.join([fecha] + manana + tarde)
        return ret


def cargar_horario():
    import json

    datos = json.load(open('datos.json', encoding='utf-8'))
    asignaturas = datos["asignaturas"]
    modificadores = datos["modificadores"]

    horario = datos['Horario']
    dias = {}

    for cod_dia, cod_turnos in horario.items():
        fecha = date.fromisoformat(cod_dia)
        turnos = []
        for cturno in cod_turnos:
            esAsig = cturno[0] in asignaturas
            if esAsig:
                key = cturno[0]
                mods = cturno[1:]
                modifs = [False] * 8
                modificadores_keys = list(modificadores.keys())
                for c in mods:
                    if c in modificadores:
                        modifs[modificadores_keys.index(c)] = True
                turno = Turno(key, modifs=modifs)
            else:
                key = cturno
                turno = Turno(otro=key)
            turnos.append(turno)
        dia = Dia(fecha, turnos)
        dias[fecha.isoformat()] = dia
    return dias