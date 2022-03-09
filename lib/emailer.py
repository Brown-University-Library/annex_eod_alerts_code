import datetime, json, logging, os, pprint, smtplib, time
from email.mime.text import MIMEText

import requests


log = logging.getLogger(__name__)


def send_mail( barcode_check_results ):
    """ Composes and sends email.
        Called by controller.manage_processing() """
    EMAIL_HOST = os.environ['ANXEODALERTS__EMAIL_HOST']
    EMAIL_PORT = os.environ['ANXEODALERTS__EMAIL_PORT']
    EMAIL_FROM = os.environ['ANXEODALERTS__EMAIL_FROM']
    EMAIL_RECIPIENTS = json.loads( os.environ['ANXEODALERTS__EMAIL_RECIPIENTS_JSON'] )
    try:
        assert type(EMAIL_HOST) == str
        assert type(EMAIL_PORT) == str
        assert type(EMAIL_FROM) == str
        assert type(EMAIL_RECIPIENTS) == list
        log.debug( f'EMAIL_HOST, ``{EMAIL_HOST}``' )
        log.debug( f'EMAIL_PORT, ``{EMAIL_PORT}``' )
        log.debug( f'EMAIL_FROM, ``{EMAIL_FROM}``' )
        log.debug( f'EMAIL_RECIPIENTS, ``{EMAIL_RECIPIENTS}``' )

        message = json.dumps( barcode_check_results, indent=2, sort_keys=True )
        s = smtplib.SMTP( EMAIL_HOST, EMAIL_PORT )
        body = f'datetime: `{str(datetime.datetime.now())}`\n\nbarcode check-results...\n\n{message}\n\n[END]'
        eml = MIMEText( f'{body}' )
        eml['Subject'] = 'end-of-day barcode check agains Alma'
        eml['From'] = EMAIL_FROM
        eml['To'] = ';'.join( EMAIL_RECIPIENTS )
        s.sendmail( EMAIL_FROM, EMAIL_RECIPIENTS, eml.as_string())
    except Exception as e:
        err = repr( e )
        log.exception( f'Problem sending mail, ``{err}``' )
    return


# def _send_mail( message ):
#     """ Sends mail; generates exception which cron-job should email to crontab owner on sendmail failure.
#         Called by run_check() """
#     log.debug( f'message, ``{message}``' )
#     try:
#         s = smtplib.SMTP( EMAIL_HOST, EMAIL_PORT )
#         body = f'datetime: `{str(datetime.datetime.now())}`\n\nlast few error-entries...\n\n{message}\n\nLog path: `{LOG_FILEPATH}`\n\n[END]'
#         eml = MIMEText( f'{body}' )
#         eml['Subject'] = 'error found in parse-alma-exports logfile'
#         eml['From'] = EMAIL_FROM
#         eml['To'] = ';'.join( EMAIL_RECIPIENTS )
#         s.sendmail( EMAIL_FROM, EMAIL_RECIPIENTS, eml.as_string())
#     except Exception as e:
#         err = repr( e )
#         log.exception( f'Problem sending mail, ``{err}``' )
#     return
