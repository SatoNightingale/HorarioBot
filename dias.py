import json
from datetime import date, timedelta

datos = json.load(open('datos.json', encoding='utf-8'))

asignaturas = datos["asignaturas"]
modificadores = datos["modificadores"]

nombre_turnos = {
    1: "Primera",
    2: "Segunda",
    3: "Tercera"
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
    def __init__(self, idAsig='0', /, otro=None, CP=False, Sem=False, Lab=False, Tall=False, Visit=False, Eval=False, LabC=False, EntT=False, RecT=False, modifs=None):
        self.id_asignatura = idAsig
        self.otro = otro
        if not modifs:
            self.modificadores = [CP, Sem, Lab, Tall, Visit, Eval, LabC, EntT, RecT]
        else:
            self.modificadores = modifs
    
    def __str__(self):
        if self.id_asignatura != '0':
            nombre_turno = asignaturas[self.id_asignatura]
        if self.otro:
            nombre_turno = self.otro
        
        extra = []

        for i, mod in enumerate(self.modificadores):
            if mod:
                extra.append(list(modificadores.values())[i])

        mods = ', '.join(extra)

        if len(extra) > 0:
            mods = f" ({mods})"

        return f"{nombre_turno}{mods}"

    def esLibre(self):
        return self.id_asignatura == '0' and not self.otro



class Dia:
    def __init__(self, fecha: date, turnos = list[Turno]):
        self.fecha = fecha
        self.turnos = turnos
    
    def __str__(self):
        fecha = f"{dias_semana[self.fecha.weekday()].capitalize()}, {self.fecha.day} de {meses[self.fecha.month]} de {self.fecha.year}"

        manana = ['Mañana']
        for i, turno in enumerate(self.turnos[0:3]):
            if not turno.esLibre():
                manana.append(f"{nombre_turnos[i+1]}: {turno}")
        
        tarde = ['Tarde']
        for i, turno in enumerate(self.turnos[3:6]):
            if not turno.esLibre():
                tarde.append(f"{nombre_turnos[i+1]}: {turno}")
        
        if len(manana) == 1: manana.clear()
        if len(tarde) == 1: tarde.clear()

        ret = '\n'.join([fecha] + manana + tarde)
        return ret


def cargar_horario():
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