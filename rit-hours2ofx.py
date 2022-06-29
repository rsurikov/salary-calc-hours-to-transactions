import csv
from datetime import datetime
from locale import currency
from logging import raiseExceptions
from pprint import pprint
from unicodedata import decimal
import decimal

employees_csv_file_path = "/Users/rsurikov/GitHub/salary-calc-hours-to-transactions/data/employees.csv"
hubstaff_csv_file_path = "/Users/rsurikov/GitHub/salary-calc-hours-to-transactions/data/hubstaff.csv"
moneypro_csv_file_path = "/Users/rsurikov/GitHub/salary-calc-hours-to-transactions/csv/moneypro.csv"

def read_csv_data(csv_file_path):
    csv_header = []
    csv_data = []
    with open(csv_file_path, mode='r') as csv_file:
        first_str = True
        for row in csv.reader(csv_file):
            if not first_str:
                csv_data.append(dict(zip(csv_header,row)))
            else:
                csv_header = row
            first_str = False
    return csv_data

def write_csv_data(csv_file_path, header, data):
    with open(csv_file_path, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter = ';', quotechar = '"')
        writer.writerow(header)
        writer.writerows(data)
    
def format_date(date):
    return  datetime.strptime(date,"%Y-%m-%d").strftime("%d %b %Y")

def time_record_to_decimal(time_string):
    (h, m, s) = time_string.split(':')
    return round((int(h) * 3600 + int(m) * 60 + int(s))/3600,2)

def get_account_id_from_email(email):
    return email.split('@')[0]

def get_employee_by_name(employees,employee_name):
    return next((employee for employee in employees if employee["Task Name"].strip() == employee_name.strip()), {})

def get_hourly_rate(employee):
    if employee["Hourly rate ($) (currency)"]:
        return float(employee["Hourly rate ($) (currency)"])
    elif employee["Hourly rate (Rub) (currency)"]:
        return float(employee["Hourly rate (Rub) (currency)"])

def get_currency(employee):
    if employee["Hourly rate ($) (currency)"]:
        return "USD"
    elif employee["Hourly rate (Rub) (currency)"]:
        return "RUB"

def calc_amount(hours, hourly_rate):
    return round(hours * hourly_rate, 2)

if __name__ == '__main__':
    hubstaff = read_csv_data(hubstaff_csv_file_path)
    employees = read_csv_data(employees_csv_file_path)
    csv_header = [
        "Date",
        "Amount",
        "Currency",
        "Account",
        "Amount received",
        "Account (to)",
        "Balance",
        "Category",
        "Description",
        "Transaction Type", 
        "Type",
        "Agent",
        "Check #",
        "Class"
    ]
    csv_data = []
    for time_record in hubstaff:
        hubstaff_member = time_record["Member"]
        if employee := get_employee_by_name(employees, hubstaff_member):
            date = time_record["Date"]
            time = time_record["Time"]
            email = employee["Email (email)"]
            hourly_rate = get_hourly_rate(employee)
            currency = get_currency(employee)
            date = format_date(date)
            hours = time_record_to_decimal(time)
            account_id = get_account_id_from_email(email)
            project = time_record["Project"]
            amount = calc_amount(hourly_rate,hours)
            if currency == "RUB":
                currency_symbol = "₽"
            elif currency == "USD":
                currency_symbol = "$"
            else:
                currency_symbol = ""
            csv_data.append([date,f"-{amount}",currency,f"{account_id}:salary:{currency.lower()}","","","","",f"{amount} ({hours}h @ {hourly_rate} {currency})","Expense","","","",f"project:{project}"])
        else:
            print(f"ERROR: cant' find employee in the CSV: {hubstaff_member}")

    write_csv_data(moneypro_csv_file_path,csv_header,csv_data)
