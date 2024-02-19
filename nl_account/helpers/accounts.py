def GET_PARTNER_BALANCE(self, partner_id,currency_id, operator,from_date=False):
    
    payable_amount = 0
    receivable_amount = 0

    def get_amount_by_account_type(account_type):
            condition = ''
            if from_date:
                condition += f" AND move.date {operator} '{from_date if type(from_date) is str else from_date.strftime('%Y-%m-%d')}'"
            self._cr.execute(f"""
                SELECT
                    SUM(line.amount_currency) AS total
                FROM
                    account_move_line AS line
                INNER JOIN
                    account_move AS move ON move.id = line.move_id
                INNER JOIN
                    account_account AS account ON account.id = line.account_id
                WHERE
                    move.state = 'posted'
                AND
                    account.account_type = %s
                AND
                    line.partner_id = %s
                AND
                    line.currency_id = %s
                {condition}
            """, (account_type,partner_id.id,currency_id.id))

            return self._cr.dictfetchone().get('total') or 0
            
    payable_amount = get_amount_by_account_type('liability_payable')
    receivable_amount = get_amount_by_account_type('asset_receivable')

    return receivable_amount + payable_amount


def GET_PARTNER_ACCOUNT_ENTRIES(self, partner_id, currency_id, company_id ,from_date=False, to_date=False):
    condition = ''
    if from_date and to_date:
        condition = f" AND (move.date BETWEEN '{from_date if type(from_date) is str else from_date.strftime('%Y-%m-%d')}' AND '{to_date if type(to_date) is str else to_date.strftime('%Y-%m-%d')}') "
    self._cr.execute(f"""
        SELECT
            DISTINCT(line.id) AS id,
            move.name AS name,
            move.ref AS ref,
            move.date AS date,
            line.name AS label,
            line.credit AS credit,
            line.debit AS debit,
            line.amount_currency AS amount_currency
        FROM
            account_move_line AS line
        INNER JOIN
            account_move AS move ON move.id = line.move_id
        INNER JOIN
            account_account AS account ON account.id = line.account_id
        WHERE
            move.state = 'posted'
        And
            move.company_id =  %s
        AND
            line.partner_id = %s
        AND
            line.currency_id = %s
        AND
            account.account_type in ('liability_payable','asset_receivable')
        {condition}
        ORDER BY
            date
    """, (company_id.id,partner_id.id,currency_id.id))
    
    data = []
    total_debits = 0
    total_credits = 0
    result  = self._cr.dictfetchall()
    balance = 0
    for res in result:
        
        debit = abs(0 if res.get('amount_currency') < 0 else res.get('amount_currency'))
        credit = abs(0 if res.get('amount_currency') > 0 else res.get('amount_currency'))
        if debit == 0:
             balance-=credit
        elif credit == 0:
             balance+=debit
        data.append({
            'name': res.get('name') or '',
            'date': res.get('date'),
            'label': res.get('label'),
            'datetime': res.get('datetime'),
            'remarks': res.get('ref') or '',
            'debit': debit,
            'credit': credit,
            'balance':balance,
            'amount_currency': res.get('amount_currency'),
        })
        total_debits += debit
        total_credits += credit
    return data, total_debits, total_credits