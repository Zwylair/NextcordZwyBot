import datetime


def get_event_datetime(nowadays_index: int, input_day_num: int, hour: int, minute: int):
    # user timezone fix
    # timezone_offset = datetime.timezone()
    # print(interaction.locale)

    # defining gap between current day and target day
    if nowadays_index < input_day_num:
        gap = input_day_num - nowadays_index
    else:
        gap = 7 - nowadays_index + input_day_num
    gap = 0 if gap == 7 else gap  # gap is week duration

    date_now = datetime.datetime.now()
    date_now = date_now.replace(hour=hour, minute=minute)
    return date_now + datetime.timedelta(days=gap)
