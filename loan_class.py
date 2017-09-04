class allLoan:
    total_loan_amount = 0
    loan_data = []
    current_time = ''

    def __init__(self, current_time):
        self.current_time = current_time

    def update_loan_amount(self, loan_amount):
        ''' Increase loan_amount
        
        :param loan_amount: Float
        '''
        self.total_loan_amount += loan_amount

    def add_loan_object(self, loan):
        ''' Add loan object into array
        
        :param loan: Loan Object
        '''
        self.loan_data.append(loan)

    def __str__(self):
        s = "allLoan data:\nTotal loan needed: %s\nCurrent time: %s\n" %(self.total_loan_amount, self.current_time)
        for loan in self.loan_data:
            s += str(loan) + "\n"
        return s

class Loan:
    id = 0
    funded_amount = 0
    loan_amount = 0
    name = ''
    expiration_date = ''
    default_url = 'https://api.kivaws.org/v1/loans/'

    def __init__(self, id, name, loan_amount, funded_amount, expiration_date):
        self.id = id
        self.name = name
        self.loan_amount = loan_amount
        self.funded_amount = funded_amount
        self.expiration_date = expiration_date

    def __str__(self):
        return "id: %s, name: %s, loan_amount: %s, funded_amount: %s" %(self.id, self.name, self.loan_amount, self.funded_amount)

    def get_url(self):
        ''' Get the url for the data
        
        :param url: String that has a url to the loan in https://api.kivaws.org/
        '''
        return self.default_url + str(self.id) + ".html"

    def remaining_fundraise(self):
        ''' Get the remaining money needed to fundraise and print the result out
        
        :param diff: float in  postive value (not really used)
        '''
        diff = self.subtract_amount()

        # Edge case, if the funded_amount > loan_amount (means overfunded), but we do not need to worry about this for this exercise.
        # if diff > 0:
        #   return "Over Funded " + diff

        if diff <= 0:
            self.print_fundraising_left(diff*-1)

        return diff*-1

    def subtract_amount(self):
        ''' Subtract the loan amount from the funded amount
        
        :return Float
        '''
        return self.funded_amount - self.loan_amount

    def print_fundraising_left(self, diff):
        ''' Print the result that still need loans
        
        :param diff: Float
        '''
        separation = 60

        print('-'*separation)
        print('Id: ' + str(self.id))
        print('Name: ' +  self.name)
        print('Expiration date (Local Timezone): ' +  str(self.expiration_date))
        print('Loan amount: ' + str(self.loan_amount))
        print('Funded amount: ' + str(self.funded_amount))
        print('Remaining amount: ' + str(diff))
        print('URL: ' + self.get_url())
