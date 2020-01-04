#!/usr/bin/env python

import sys, csv, locale, pytz
from ofxtools.models import *
from ofxtools.Types import *
from ofxtools.utils import UTC
from decimal import Decimal
from datetime import datetime
import xml.etree.ElementTree as ET
from ofxtools.header import make_header

locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

def parse_row(row):
    now = datetime.today()
    date = datetime.strptime(row[0], "%d/%b")
    if date.month <= now.month:
        date = date.replace(year=now.year)
    else:
        date = date.replace(year=now.year-1)
    date = pytz.UTC.localize(date)

    description = row[1]
    if row[2] == "Crédito":
        type = "CREDIT"
    elif row[2] == "Débito":
        type = "DEBIT"
    else:
        type = "OTHER"

    amount = round(Decimal(row[3].replace('R$', '').replace(' ', '').replace('.', '').replace(',', '.')), 2)
    return STMTTRN(trntype=type, trnamt=amount, memo=description, dtposted=date, fitid='0000')


if len(sys.argv) != 2:
    print("Usage: %s [csv file]" % (sys.argv[0]))
    sys.exit(1)

infile = sys.argv[1]

header_columns = ["DATA", "HISTÓRICO DE DESPESAS", "TIPO", "VALOR"]
transactions = []
dtstart = None
dtend = None
utctoday = pytz.UTC.localize(datetime.today())

with open(infile, encoding='ISO-8859-1') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=';')
    line_count = 0
    for row in csv_reader:
        if line_count == 0:
            if header_columns != row:
                print(f'Invalid header: {",".join(row)}. Expected: {",".join(header_columns)}')
                sys.exit(2)
            line_count += 1
        else:
            transaction = parse_row(row)
            if dtstart is None or transaction.dtposted < dtstart:
                dtstart = transaction.dtposted

            if dtend is None or transaction.dtposted > dtend:
                dtend = transaction.dtposted

            transactions.append(parse_row(row))
            line_count += 1

ledgerbal = LEDGERBAL(balamt=Decimal('0'), dtasof=utctoday)
acctfrom = BANKACCTFROM(bankid='212', acctid='000000', accttype='CHECKING')  # OFX Section 11.3.1
banktranlist = BANKTRANLIST(*transactions, dtstart=dtstart, dtend=dtend)
stmtrs = STMTRS(curdef='BRL', bankacctfrom=acctfrom, ledgerbal=ledgerbal, banktranlist=banktranlist)

status = STATUS(code=0, severity='INFO')
stmttrnrs = STMTTRNRS(trnuid='1', status=status, stmtrs=stmtrs)

bankmsgsrs = BANKMSGSRSV1(stmttrnrs)

# Institutional info
fi = FI(org='ORIGINAL', fid='ORIGINAL')
sonrs = SONRS(status=status, dtserver=utctoday, language='ENG', fi=fi)
signonmsgs = SIGNONMSGSRSV1(sonrs=sonrs)

ofx = OFX(signonmsgsrsv1=signonmsgs, bankmsgsrsv1=bankmsgsrs)

root = ofx.to_etree()
message = ET.tostring(root).decode()
header = str(make_header(version=102))
response = header + message

print(response)

