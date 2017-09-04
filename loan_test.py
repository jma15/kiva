import unittest
from loan import *

# A small set of data from Kiva Api
mock_data= [{
                u'loanAmount': u'5525.00', 
                u'loanFundraisingInfo': 
                    {u'fundedAmount': u'750.00'}, 
                u'plannedExpirationDate': u'2017-10-03T20:20:02Z', 
                u'name': u'San Rafael Group', 
                u'id': 1366881}, 
            {
                u'loanAmount': u'5650.00', 
                u'loanFundraisingInfo': {u'fundedAmount': u'750.00'}, 
                u'plannedExpirationDate': u'2017-10-03T20:00:03Z', 
                u'name': u'Nueva Esperanza Group', 
                u'id': 1366878}, 
            {
                u'loanAmount': u'4025.00', 
                u'loanFundraisingInfo': {u'fundedAmount': u'1500.00'}, 
                u'plannedExpirationDate': u'2017-10-01T15:20:02Z', 
                u'name': u'Maria Auxiliadora Group', 
                u'id': 1365895
            }]

# Use our timezone for convenience
tz = pytz.timezone('America/Los_Angeles')
# We will use 2017-10-02, because the above dataset has two dates in 2017-10-03
current_time = datetime.datetime(2017, 10, 2, 21, 44, 30, 801000)
current_time = pytz.utc.localize(current_time, is_dst=None).astimezone(tz)

# Test most of the functions
class TestScriptMethods(unittest.TestCase):
    # Check for https request, query, and data is valid
    def test_request_data(self):
        query = graphql_query()
        data = request_data(query)

        # If there is data
        if data[0]:
            data = data[0]
            # Verify the request returns these parameters
            self.assertTrue("loanAmount" in data)
            self.assertTrue("loanFundraisingInfo" in data)
            self.assertTrue("plannedExpirationDate" in data)
            self.assertTrue("id" in data)

    # Check time conversion works with the first 'plannedExpirationDate'
    def test_cast_utc_to_local(self):
        expected_date = '2017-10-03 13:20:02-07:00'
        date_string = mock_data[0]['plannedExpirationDate']
        actual_date = str(cast_utc_to_local(date_string, tz))
        self.assertEqual(expected_date, actual_date)

    # Check date is one day away
    def test_check_within_one_day(self):
        # Only 20 hours away
        expected_bool = True
        current = datetime.datetime(2017, 10, 2, 3, 44, 30, 801000)
        future = datetime.datetime(2017, 10, 2, 23, 44, 30, 801000)
        actual_bool = check_within_one_day(current, future)
        self.assertEqual(expected_bool, actual_bool)

        # This is 10 days away
        expected_bool = False
        current = datetime.datetime(2017, 10, 2, 3, 44, 30, 801000)
        future = datetime.datetime(2017, 10, 12, 3, 44, 30, 801000)
        actual_bool = check_within_one_day(current, future)
        self.assertEqual(expected_bool, actual_bool)

    # Test main function to see if the code returns right calculation and and right values
    # We will use some static variables, current time, timezone and api data from above
    # because these dataset will constantly change.
    def test_find_total_amount(self):
        # This class will hold all the information we need for comparison
        all_loan = find_total_amount(mock_data, current_time, tz, False)

        # Check to see if summation is correct
        expected_total_loan = 11175
        actual_total_loan = all_loan.total_loan_amount
        self.assertEqual(expected_total_loan, actual_total_loan)

        # There should be 2 rows
        expected_loan_count = 2
        actual_loan_count = len(all_loan.loan_data)
        self.assertEqual(expected_loan_count, actual_loan_count)

        # Check the links for each loans
        expected_url_one = 'https://api.kivaws.org/v1/loans/1366881.html'
        actual_url_one = all_loan.loan_data[0].get_url()
        self.assertEqual(expected_url_one, actual_url_one)

        expected_url_two = 'https://api.kivaws.org/v1/loans/1366878.html'
        actual_url_two = all_loan.loan_data[1].get_url()
        self.assertEqual(expected_url_two, actual_url_two)

        # Check amount it has left to fundraise for each loans
        expected_loan_left_one = -4775
        actual_loan_left_one = all_loan.loan_data[0].subtract_amount()
        self.assertEqual(expected_loan_left_one, actual_loan_left_one)

        expected_loan_left_two = -4900
        actual_loan_left_two = all_loan.loan_data[1].subtract_amount()
        self.assertEqual(expected_loan_left_two, actual_loan_left_two)

# Test the basic functionality of the class
class TestClassMethods(unittest.TestCase):
    def test_loans_class(self):
        # Test the allLoans class
        # Declare the class and clear the variables
        all_loan = allLoan(current_time)
        all_loan.loan_data = []

        # Test update loan function
        all_loan.update_loan_amount(200.30)
        all_loan.update_loan_amount(300.40)
        expected_loan_amount = 500.70
        self.assertEqual(expected_loan_amount, all_loan.total_loan_amount)

        # Test insert function
        loan_obj = Loan(1, 'Test', 600, 600, datetime.datetime(2017, 10, 2, 3, 44, 30, 801000))
        all_loan.add_loan_object(loan_obj)
        self.assertEqual(1, len(all_loan.loan_data))

        # Verify the insert data is correct
        self.assertEqual(1, all_loan.loan_data[0].id)
        self.assertEqual('Test', all_loan.loan_data[0].name)
        self.assertEqual(600, all_loan.loan_data[0].loan_amount)

        # Test the loans class function (Individually, similar to previous test)
        # Test the subtract function
        self.assertEqual(0, all_loan.loan_data[0].subtract_amount())
        # Test the url function
        self.assertEqual('https://api.kivaws.org/v1/loans/1.html',all_loan.loan_data[0].get_url())


if __name__ == '__main__':
    unittest.main()