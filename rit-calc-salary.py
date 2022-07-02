import pandas as pd

employees_csv_file_path = "/Users/rsurikov/GitHub/salary-calc-hours-to-transactions/data/employees.csv"
hubstaff_csv_file_path = "/Users/rsurikov/GitHub/salary-calc-hours-to-transactions/data/hubstaff.csv"
hourly_csv_file_path = "/Users/rsurikov/GitHub/salary-calc-hours-to-transactions/csv/hourly.csv"

def get_hubstaff_alias(name):
    aliases = {
        "Lera Sablina": "Valeriya Sablina",
        "Nikita Kryuchkov": "Nikita Kruchkov",
        "Vasily Eliseev": "Vasilii Eliseev",
    }
    return aliases.get(name, name)

def time_to_hours(time_string):
    (h, m, s) = time_string.split(':')
    return round((int(h) * 3600 + int(m) * 60 + int(s))/3600,2)

def calc_salary_amount(hours, hourly_rate):
    return round(hours * hourly_rate, 2)

def get_employee_username_by_email(email):
    return email.split('@')[0]

def get_employee_by_name(name,employees):
    employee = {
        "name": name,
        "type": None,
        "value": None,
        "currency": None,
        "email": None,
        "vacation": None
    }
    name = get_hubstaff_alias(name)
    hourly_usd = employees.loc[(employees['Name'] == name) & ~employees['Hourly Rate USD'].isna()]
    hourly_rub = employees.loc[(employees['Name'] == name) & ~employees['Hourly Rate RUB'].isna()]
    if not hourly_usd.empty or not hourly_rub.empty:
        employee["type"] = "hourly"
        if hourly_usd.empty:
            employee["vacation"] = hourly_rub.iloc[0]['Vacation %']
            employee["email"] = hourly_rub.iloc[0]['Email']
            employee["value"] = hourly_rub.iloc[0]['Hourly Rate RUB']
            employee["currency"] = "RUB"
        else:
            employee["vacation"] = hourly_usd.iloc[0]['Vacation %']
            employee["email"] = hourly_usd.iloc[0]['Email']
            employee["value"] = hourly_usd.iloc[0]['Hourly Rate USD']
            employee["currency"] = "USD"
    else: 
        print(f"ERROR: cant' find salary for employee: {name}") 
    return employee

employees_col = ['ID', 'Name', 'Email', 'Hourly Rate USD', 'Hourly Rate RUB',
                'Monthly Rate USD', 'Monthly Rate RUB', 'Vacation %',]

transactions_col = ['Date', 'Amount', 'Currency', 'Account', 'Description', 
                'Class','Category']

employees = pd.read_csv(employees_csv_file_path, names=employees_col, skiprows=[0])
time_records = pd.read_csv(hubstaff_csv_file_path)

transactions = pd.DataFrame(columns = transactions_col)

new_index = 0
for index, time_record in time_records.iterrows():
    employee = get_employee_by_name(time_record["Member"],employees)
    if employee["type"] == "hourly":
        hours = time_to_hours(time_record["Time"])
        amount = calc_salary_amount(hours,employee["value"])
        if amount > 0:
            user_name = get_employee_username_by_email(employee["email"])
            account_salary = f"{user_name}:salary:{employee['currency'].lower()}"
            description = f"{amount} {employee['currency']} ({hours}h @ {employee['value']} {employee['currency'].lower()}) - {time_record['Project']}"
            category = f"project:{time_record['Project']}"
            transactions.loc[new_index] = [time_record["Date"],-1 * amount,employee["currency"],account_salary,description,category,category]
            vacation_p = float(employee['vacation'])
            if vacation_p > 0:
                description_vacation = f"{float(employee['vacation'])*100}% of {description}"
                account_vacation = f"{user_name}:vacation:{employee['currency'].lower()}"
                new_index += 1
                transactions.loc[new_index] = [time_record["Date"],-1 * round(employee["value"]*employee["vacation"],2),employee["currency"],account_vacation,description_vacation,category,category]
            new_index += 1
transactions.to_csv(hourly_csv_file_path, sep = ";", index = False)