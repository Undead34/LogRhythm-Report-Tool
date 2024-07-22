import calendar

def get_human_readable_period(start_date, end_date):
    month_translation = {
        'January': 'enero', 'February': 'febrero', 'March': 'marzo', 'April': 'abril', 
        'May': 'mayo', 'June': 'junio', 'July': 'julio', 'August': 'agosto', 
        'September': 'septiembre', 'October': 'octubre', 'November': 'noviembre', 'December': 'diciembre'
    }
    
    start_month = calendar.month_name[start_date.month]
    end_month = calendar.month_name[end_date.month]
    start_month_es = month_translation[start_month]
    end_month_es = month_translation[end_month]
    start_date_str = start_date.strftime(f'%d de {start_month_es} de %Y')
    end_date_str = end_date.strftime(f'%d de {end_month_es} de %Y')
    
    return start_date_str, end_date_str
