import requests
import json
import datetime
import pytz
from tzlocal import get_localzone
import getopt
import sys
from loan_class import *

# link to loans data individual
# r = requests.get('https://api.kivaws.org/v1/loans/2930.json')

def cast_utc_to_local(date, local_tz):
    ''' Cast utc time to local timezone
    
    :param date: Datetime object
    :param local_tz: timezone object
    :return: Datetime object with local_tz timezone
    '''
    date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
    date = pytz.utc.localize(date, is_dst=None).astimezone(local_tz)
    return date

def check_within_one_day(current_date, future_date):
    ''' Check if future date is within 24 hours
    
    :param current_date: Datetime object of current date
    :param future_date: Datetime object of a date in the future
    :return: Boolean
    '''

    # Base case, the future date already passed. We want < 24 hours ahead of current date
    if future_date < current_date:
        return False

    if (future_date - current_date) < datetime.timedelta(days=1):
        return True

    return False

def graphql_query():
    ''' Query for the graphql http GET request

    :return: String with graphql query
    '''

    # Query to obtain all status of 'fundRaising'
    query = '''
    {
        loans(filters: {status: fundRaising}) {
            totalCount
            values {
                name
                loanAmount
                plannedExpirationDate
                id
                loanFundraisingInfo {
                  fundedAmount
                }
            }
        }
    }
            '''

    return query    

def request_data(query):
    ''' Query Kiva api and return the json data

    :return: JSON with graphql data
    '''
    # Example URL is http://myapi/graphql?query={me{name}}
    r = requests.get('http://api.kivaws.org/graphql?query=' + query)
    data = r.json()

    if 'data' in data:
        data = data['data']['loans']['values']
    else:
        print("Something is wrong, there is no Data from query.")
        sys.exit(2)

    return data

def get_timezone():
    ''' Function to get the current timezone

    :return: timezone object
    '''

    # Example of local timezone
    # America/New_York
    # America/Los_Angeles
    # Get current timezone

    tz = get_localzone()
    # Set pytz with current timezone
    tz = pytz.timezone(str(tz))
    return tz

def get_time(tz):
    ''' Function to get the current time in timezone
    
    :param tz: timezone object from function get_timezone()

    :return: dateTime object
    '''

    # Current time in utc
    current_time = datetime.datetime.now(tz)

    # # Testing data for different time. (This is changed to opts parameter)
    # current_time = datetime.datetime(2017, 10, 2, 23, 44, 30, 801000)
    # current_time = tz.localize(current_time)

    return current_time

def find_total_amount(data, current_time, tz, print_data):
    ''' Core function of the script to filter data from Kiva Api

    Loop through the data from the api. If the 'plannedExpirationDate' is within 24 hours of the 
    current_time provided, store the loan_amount, and other information into the loan_class.py 
    classes.
    
    :param data: JSON object from the Kiva
    :param current_time: dateTime to check within 24 hours of
    :param tz: timezone object from function get_timezone() to localize date from json

    :return: allLoan object
    '''

    # Declare class to hold all data
    all_loan = allLoan(current_time)

    for l in data:
        # Collecting and format data from unicode to the correct format
        loan_amount = float(l['loanAmount'])
        funded_amount = float(l['loanFundraisingInfo']['fundedAmount'])
        id = int(l['id'])
        # Have to encode the unicode back to text
        name = l['name'].encode('utf-8').strip()
        # This is UTC datetime in ISO8601 format, cast the date to OUR current timezone
        expiration_date = l['plannedExpirationDate']
        expiration_date = cast_utc_to_local(expiration_date, tz)

        # If the date is within 24 hours of deadline, we want the data, else disregard it
        if check_within_one_day(current_time, expiration_date):
            # sum up all the loans
            loan_obj = Loan(id, name, loan_amount, funded_amount, expiration_date)
            all_loan.update_loan_amount(loan_amount)
            all_loan.add_loan_object(loan_obj)
            # print the remaining data
            if print_data:
                loan_obj.remaining_fundraise()

    return all_loan

def print_results(all_loan,tz):
    ''' Function to print final results from the all_loan class to console.

    :param all_loan: allLoan object with data from Kiva api
    :param tz: timezone object from function get_timezone()

    '''

    print('='*60)

    print("Current local timezone: " + str(tz))
    print("Results for date: " + str(all_loan.current_time))
    print("Total number of loans: " + str(len(all_loan.loan_data)))
    print("Total amount of money needed: $%.2f" % all_loan.total_loan_amount)

def check_opts(tz):
    ''' Function to check for user argument to see if date is provided. Invalid parameters
    will exit the script. If the parameter is valid, but the date failed to parse then use
    current time with local timezone.

    Allow two types of execution:
        python loan.py
    OR
        python loan.py -d 'YEAR-MONTH-DAY HOUR:MINUTE:SEC'
        Example:
            python loan.py -d '2017-09-08 23:44:30'

    :param tz: timezone object from function get_timezone()

    :return: dateTime object of either user input or current time

    '''
    args = sys.argv[1:]
    current_time = ''
    try:
        opts, args = getopt.getopt(args, 'd:', [])
    except getopt.GetoptError:
        print("Please enter the valid format:")
        print("python loan.py")
        print("python loan.py -d '2017-09-08 23:44:30'")
        # Exit the script
        sys.exit(2)

    # Check the opt parameter for a datetime
    for opt, arg in opts:
        if opt == '-d':
            # We want this format 2017-09-08 23:44:30 and also localize to current timezone
            try:
                datetime_object = datetime.datetime.strptime(arg, '%Y-%m-%d %H:%M:%S')
                datetime_object = tz.localize(datetime_object)
                current_time = datetime_object
            except ValueError:
                # Unable to use user input, default time as current time
                print("Unable to parse input date " + arg)


    if not current_time:
        print("Default to current time")
        current_time = get_time(tz)

    return current_time
# Main function
def main():
    tz = get_timezone()
    current_time = check_opts(tz)
    query = graphql_query()
    data = request_data(query)
    all_loan = find_total_amount(data, current_time, tz, True)
    print_results(all_loan, tz)

# Start the main function
if __name__ == "__main__":
    main()
