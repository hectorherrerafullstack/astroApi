# Datos calculados vs proporcionados para Persona 2
calculated = {
    'Sun': (25, 21, 55),
    'Moon': (6, 2, 18),
    'Mercury': (27, 17, 51),
    'Venus': (25, 12, 56),
    'Mars': (27, 25, 3),
    'Jupiter': (11, 29, 58),
    'Saturn': (11, 7, 40),
    'Uranus': (16, 13, 1),
    'Neptune': (17, 50, 5),
    'Pluto': (22, 55, 35),
    'Asc': (21, 5, 50),
    'MC': (19, 36, 1),
    'True Node': (8, 55, 53),
    'Chiron': (5, 9, 45)
}

provided = {
    'Sun': (25, 21, 45),
    'Moon': (6, 2, 18),
    'Mercury': (27, 17, 51),
    'Venus': (25, 12, 56),
    'Mars': (27, 25, 3),
    'Jupiter': (11, 29, 58),
    'Saturn': (11, 7, 40),
    'Uranus': (16, 13, 1),
    'Neptune': (17, 50, 5),
    'Pluto': (22, 55, 35),
    'Asc': (21, 5, 0),
    'MC': (19, 36, 0),
    'True Node': (8, 55, 35),
    'Chiron': (5, 9, 45)
}

def to_seconds(deg, min, sec):
    return deg * 3600 + min * 60 + sec

print('Diferencias en segundos de arco:')
total_diff = 0
count = 0
for key in calculated:
    calc_sec = to_seconds(*calculated[key])
    prov_sec = to_seconds(*provided[key])
    diff = abs(calc_sec - prov_sec)
    total_diff += diff
    count += 1
    print(f'{key}: {diff}"')

avg_diff = total_diff / count
print(f'\nDiferencia promedio: {avg_diff:.2f}" de arco')
print(f'Equivalente a ~{avg_diff/60:.2f} minutos de arco')