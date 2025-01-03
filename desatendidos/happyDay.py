from datetime import date

def happyf(fechana):
    print('+++++++++++++')
    print(fechana)
    hoy = date.today()
    fecha_final = fechana
    try:            
        fecha = fecha_final.replace(year=hoy.year)            
        if hoy <= fecha:
            dif = fecha - hoy
            happy = dif.days
        else:
            fecha = fecha.replace(year=hoy.year + 1 )
            dif = fecha - hoy
            happy = dif.days
    except Exception as e:
        print(str(e))
        happy = 'No tiene FN'
    print(happy)
    return str(happy)