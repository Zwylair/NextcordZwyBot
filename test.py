from datetime import datetime, timedelta

date = datetime.now() + timedelta(seconds=65)
timestamp = f'{date.timestamp()}'.split('.')[0]

print(f'<t:{timestamp}:R>')
