import pandas as pd

data = {
    "HR/DIA": ["08:00 A 09:30", "09:40 A 11:10", "11:20 A 12:50", "08:00 A 09:30"],
    "TORRE": ["TORRE A", "TORRE A", "TORRE B", "TORRE A"],
    "AULA": ["A1", "A1", "B1", "A2"],
    "LUNES": ["DOCENTE: JUAN PEREZ MATERIA: MATEMATICAS", "LIBRE", "DOCENTE: MARIA LOPEZ MATERIA: FISICA", "DOCENTE: JUAN PEREZ MATERIA: QUIMICA"],
    "MARTES": ["LIBRE", "DOCENTE: ANA GOMEZ MATERIA: PROGRAMACION", "LIBRE", "LIBRE"]
}
df = pd.DataFrame(data)
df.to_excel("datos_horarios/test_horarios.xlsx", index=False)
print("Dummy excel file created at datos_horarios/test_horarios.xlsx")
