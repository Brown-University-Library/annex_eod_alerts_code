'''
This script:
- Takes a filepath and email address
- Loads up the barcodes, and for each barcode...
    - Performs a GET lookup and stores the original data
    - Executes a PUT change and stores the resulting data
- Constructs a CSV with results
- Emails the CSV as en attachment

Usage...
- assumes:
    - five required environmental-variables are set (see below, after logging config)
- % cd ./annex_eod_alerts_code
- % source ../env/bin/activate
- % python3 ./lib/script_file_path_to_csv.py --email the-email-address --file_path /the/path.txt
'''

import argparse, csv, io, logging, os, pathlib, pprint, smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests


logging.basicConfig(
    # filename=zzz,
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger(__name__)
log.debug( 'logging ready' )


ENVAR_SMTP_HOST: str = os.environ[ 'ANXEODALERTS__EMAIL_HOST' ]
ENVAR_SMTP_PORT: str = os.environ[ 'ANXEODALERTS__EMAIL_PORT' ]


def manage_barcode_processing( file_path: str, emails: list ) -> None:
    temp__send_mail( emails )
    return


def temp__send_mail( emails: list ) -> None:
    """ Tests build of email with a CSV attachment.
        Called by manage_csv_email() 
        TODO test multiple attachments. """
    ## setup
    EMAIL_SUBJECT: str = 'The Subject'
    # EMAIL_FROM: str = os.environ[ 'ANXEODALERTS__TEST_EMAIL_FROM' ]
    EMAIL_FROM: str = 'donotreply_annex-end-of-day-reports@brown.edu'
    # EMAIL_TO = os.environ[ 'ANXEODALERTS__TEST_EMAIL_TO_STRING' ]
    emails_str: str = ','.join( emails )
    EMAIL_TO: str = emails_str
    # EMAIL_TO: list = emails
    MESSAGE_BODY: str = 'The message body.'
  
    SMTP_SERVER: str = ENVAR_SMTP_HOST
    SMTP_PORT: int = int( ENVAR_SMTP_PORT )
    ## create multipart message
    msg = MIMEMultipart()
    # body_part = MIMEText(MESSAGE_BODY, _subtype='plain', _charset='utf-8' )
    # body_part = MIMEText(MESSAGE_BODY, _subtype='plain', _charset='ascii' )
    msg['Subject'] = EMAIL_SUBJECT
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    ## add body to email
    # msg.attach(body_part)
    ## create SMTP object
    smtp_obj = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    ## send mail
    smtp_obj.sendmail( msg['From'], emails, msg.as_string() )
    smtp_obj.quit()
    return

    ## end def temp__send_mail()



def parse_args() -> dict:
    """ Parses arguments when module called via __main__ """
    parser = argparse.ArgumentParser( description='Required: file_path and email (comma-separated if multiple).' )
    parser.add_argument( '--file_path', '-f', help='file_path required', required=True )
    parser.add_argument( '--email', '-e', help='email (comma-separated if multiple) required', required=True )
    args: dict = vars( parser.parse_args() )
    return args


if __name__ == '__main__':
    args: dict = parse_args()
    log.debug( f'args, ```{args}```' )
    file_path: str = args['file_path']
    email_str: str = args['email']
    emails: list = email_str.split( ',' )
    log.debug( f'emails, ``{emails}``' )
    manage_barcode_processing( file_path, emails )



