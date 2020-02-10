import requests
import lxml.html as html
import sys as system
import datetime as datetime
import xlsxwriter as xlsx
import logging as log
import traceback


def get_years():

    for i in h1Elements:
        _h1_str = i.text_content()

    _h1_tmp = _h1_str.split()
    _years = _h1_tmp[0].split('-')
    _start_year = _years[0]
    _end_year = _years[1]

    if _start_year[0] == '2':
        _end_year = '20' + _years[1]
    else:
        if _end_year == '00':
            _end_year = '20' + _years[1]
        else:
            _end_year = '19' + _years[1]

    return [_start_year, _end_year]


def get_header(_years_list):

    for i in h1Elements:
        _h1_str = i.text_content()

    _h1_tmp = _h1_str.split()
    _header = " ".join(_h1_tmp)
    _header = _header.split()
    _header[0] = _years_list[0] + '-' + _years_list[1]

    return " ".join(_header)


def get_day_of_week(y, m, d):

    _weekDays = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
    _day = datetime.date(y, m, d)
    _dayNum = _day.weekday()

    return _weekDays[_dayNum]


def get_scrape_team(_header):

    _header_split = _header.split()
    _team = _header_split[2]

    if _team == 'York' or _team == 'Jersey' or _team == 'Bay' or _team == 'Louis' or _team == 'Jose' or _team == 'Angeles':
        return _header_split[3]

    if _team == 'Blue' or _team == 'Maple' or _team == 'Red' or _team == 'Golden':
        return _header_split[2] + ' ' + _header_split[3]

    return _team


def get_only_team_name(_full_team):

    _team_split = _full_team.split()

    _team = _team_split[1]

    if _team == 'York' or _team == 'Jersey' or _team == 'Bay' or _team == 'Louis' or _team == 'Jose' or _team == 'Angeles':
        return _team_split[2]

    if _team == 'Blue' or _team == 'Maple' or _team == 'Red' or _team == 'Golden':
        return _team_split[1] + ' ' + _team_split[2]

    return _team


def get_month_abbr(_month):

    switcher = {
        10: 'Oct',
        11: 'Nov',
        12: 'Dec',
        1: 'Jan',
        2: 'Feb',
        3: 'Mar',
        4: 'Apr',
        5: 'May',
        6: 'June'
    }
    return switcher.get(_month, "xxx")


def get_date(_date):

    _date_split = _date.split('-')
    _month = int(_date_split[1])
    _year = int(_date_split[0])
    _day = int(_date_split[2])

    _day_abbr = get_day_of_week(_year, _month, _day)
    _month_abbr = get_month_abbr(_month)

    return _day_abbr + ',' + ' ' + str(_day) + ' ' + _month_abbr + ' ' + str(_year)


def get_score(_gf, _ga, _ot_so):

    if not _gf and not _ga:
        return ' '

    return _gf + ' ' + '-' + ' ' + _ga + ' ' + _ot_so


def get_time(_time_str, _tzone):

    if _tzone == 'MT':
        _zne_num = 2
    elif _tzone == 'CT':
        _zne_num = 1
    else:
        _zne_num = 0

    hm_arr = _time_str.split(':')
    m_ampm_arr = hm_arr[1].split()
    time_day = m_ampm_arr[1]

    _min = m_ampm_arr[0]
    _hour = int(hm_arr[0])

    est_24hour = to_24hour(_hour, time_day)

    _hour, _ampm = to_12hour((est_24hour - _zne_num + 24) % 24)

    return str(_hour) + ':' + _min + ' ' + _ampm


def to_24hour(_hour, _ampm):

    if _ampm == 'am':
        return 0 if _hour == 12 else _hour
    else:
        return 12 if _hour == 12 else _hour + 12


def to_12hour(_hour):

    if _hour == 0:
        return 12, 'AM'
    elif _hour < 12:
        return _hour, 'AM'
    elif _hour == 12:
        return 12, 'PM'
    else:
        return _hour - 12, 'PM'


def write_column_header(row_val, is_cur_szn):

    _date = 'Date'
    _visitor = 'Visitor'
    _home = 'Home'
    _score = 'Score'
    _dec = 'Dec'
    _time = 'Time (' + usersZone + ')'

    if is_cur_szn:
        _row = (_date, _visitor, _home, _score, _dec, _time)
        worksheet.write_row(row_val, _row)
    else:
        _row = (_date, _visitor, _home, _score, _dec)
        worksheet.write_row(row_val, _row)


def write_month_header(row_val, _mon):

    if curMonth == 11:
        worksheet.write(row_val, monthHeaders[1])
    if curMonth == 12:
        worksheet.write(row_val, monthHeaders[2])
    if curMonth == 13:
        worksheet.write(row_val, monthHeaders[3])
    if curMonth == 14:
        worksheet.write(row_val, monthHeaders[4])
    if curMonth == 15:
        worksheet.write(row_val, monthHeaders[5])
    if curMonth == 16:
        worksheet.write(row_val, monthHeaders[6])
    if curMonth == 17:
        worksheet.write(row_val, monthHeaders[7])
    if curMonth == 18:
        worksheet.write(row_val, monthHeaders[8])


def validate_team(_team):

    _lowercase_team = _team.lower()

    d = {
        'ducks': 'ANA',
        'coyotes': 'ARI',
        'bruins': 'BOS',
        'sabres': 'BUF',
        'flames': 'CGY',
        'hurricanes': 'CAR',
        'blackhawks': 'CHI',
        'avalanche': 'COL',
        'blue jackets': 'CBJ',
        'stars': 'DAL',
        'red wings': 'DET',
        'oilers': 'EDM',
        'panthers': 'FLA',
        'kings': 'LAK',
        'wild': 'MIN',
        'canadiens': 'MTL',
        'predators': 'NSH',
        'devils': 'NYD',
        'islanders': 'NYI',
        'rangers': 'NYR',
        'senators': 'OTT',
        'flyers': 'PHI',
        'penguins': 'PIT',
        'shatks': 'SJS',
        'blues': 'STL',
        'lightning': 'TBL',
        'maple leafs': 'TOR',
        'canucks': 'VAN',
        'golden knights': 'VEG',
        'capitals': 'WSH',
        'jets': 'WPG',
    }

    return d.get(_lowercase_team, 'NO')


if __name__ == '__main__':

    log.basicConfig(filename='scrapeLog.log', format='%(asctime)s %(message)s', level=log.INFO)
    log.info('Application STARTED -------')
    print('Example of team names: Flames, Blues, Islanders ...\n')

    while 1:

        userInput = input('Enter a team name ("q" to quit): ')

        if userInput == 'q' or userInput == 'Q':
            log.info('Closing application (user entered q/Q)')
            system.exit()

        userTeam = validate_team(userInput)

        if userTeam != 'NO':
            userYear = input('Enter the year you would like: ')
            url = 'https://www.hockey-reference.com/teams/' + userTeam + '/' + userYear + '_games.html'
            usersZone = input("Enter a desired time zone (MT, EST, CT): ")
            break

    try:

        page = requests.get(url)

        doc = html.fromstring(page.content)
        trElements = doc.xpath('//tr')
        h1Elements = doc.xpath('//h1')

        years = get_years()  # start and end year

        atColumn = 3
        oppColumn = 4
        gfColumn = 5
        gaColumn = 6
        decColumn = 7
        otsoColumn = 8

        if len(trElements[0]) == 16:
            currentSeason = True
        else:
            atColumn -= 1
            oppColumn -= 1
            gfColumn -= 1
            gaColumn -= 1
            decColumn -= 1
            otsoColumn -= 1
            currentSeason = False

        header = get_header(years)  # header for excel sheet

        columns = ['Date', 'Visitor', 'Home', 'Score', 'Dec', 'Time']
        monthHeaders = ['OCTOBER ' + years[0], 'NOVEMBER ' + years[0], 'DECEMBER ' + years[0], 'JANUARY ' + years[1],
                        'FEBRUARY ' + years[1], 'MARCH ' + years[1], 'APRIL ' + years[1], 'MAY ' + years[1], 'JUNE ' + years[1]]

        scrape_team = get_scrape_team(header)  # team you are scraping for

        workbookName = years[0] + years[1] + scrape_team + '.xlsx'
        workbook = xlsx.Workbook(workbookName)
        worksheet = workbook.add_worksheet()

        worksheet.write('A1', str(header))  # add header to excel sheet
        worksheet.write('A2', monthHeaders[0])  # add october month header
        write_column_header('A3', currentSeason)  # add column headers

        j = 0  # row index value for table
        r = 4  # index value for excel
        curMonth = 10

        while j < len(trElements):  # logic to iterate through tables row <tr> tags

            if trElements[j][0].text_content() == 'GP':
                j += 1
                continue

            date = get_date(trElements[j][1].text_content())

            tmpDate = trElements[j][1].text_content().split('-')
            tmpMonth = int(tmpDate[1])
            if tmpMonth == 1 or tmpMonth == 2 or tmpMonth == 3 or tmpMonth == 4 or tmpMonth == 5 or tmpMonth == 6:
                tmpMonth += 12

            if tmpMonth > curMonth:
                curMonth = tmpMonth
                cellRow = 'A' + str(r)
                write_month_header(cellRow, curMonth)
                r += 1
                cellRow = 'A' + str(r)
                write_column_header(cellRow, currentSeason)
                r += 1

            if trElements[j][atColumn].text_content() == '@':  # check if away game
                visitor = scrape_team
                home = get_only_team_name(trElements[j][oppColumn].text_content())
            else:
                visitor = get_only_team_name(trElements[j][oppColumn].text_content())
                home = scrape_team

            ot_so = trElements[j][otsoColumn].text_content()

            score = get_score(trElements[j][gfColumn].text_content(), trElements[j][gaColumn].text_content(), ot_so)

            dec = trElements[j][decColumn].text_content()

            excelRow = 'A' + str(r)

            if currentSeason:
                time = get_time(trElements[j][2].text_content(), usersZone)
                row = (date, visitor, home, score, dec, time)
            else:
                row = (date, visitor, home, score, dec)

            worksheet.write_row(excelRow, row)

            j += 1

            r += 1

        workbook.close()
        log.info('Succesfully created .xlsx file: %s', workbookName)
        created = True

    except Exception as ex:
        created = False
        stacktrace = traceback.format_exc()
        log.info('URL: %s | Exception stack trace: %s', url, stacktrace)

    finally:
        if created:
            input('Successfully crated schedule! Press "Enter" to quit')
        else:
            input('Oops we encountered an error! Press "Enter" to quit')

        log.info('Application CLOSED -------')
        system.exit()