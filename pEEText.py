# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


def defineLoggers(cfile, today, logs_name):
    import logging
    from os import path, makedirs
    absfile = path.dirname(path.abspath(cfile))
    dirname = absfile + '\\logs\\'
    if not path.exists(dirname):
        makedirs(dirname)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.disabled = False
    try:
        handler = logging.FileHandler(dirname + logs_name + '_info_' +
                                      today.strftime("%Y-%m-%d") + '.log')
        handler.setLevel(logging.INFO)
        handlerErr = logging.FileHandler(dirname + logs_name + '_errors_' +
                                         today.strftime("%Y-%m-%d") + '.log')
        handlerErr.setLevel(logging.ERROR)
    except:
        logging.error('defineLoggers:Log file cannot be created')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(processName)s - '
                                  '%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    handlerErr.setFormatter(formatter)
    logger.addHandler(handler)
    logger.addHandler(handlerErr)
    logger.info(('*************** Starting ' + logs_name + ', time: %s '
                 '*************** \n' % (today.strftime("%Y-%m-%d"))))
    return (logger, handler, handlerErr)

def closeLoggers(logger, handler, handlerErr):
    handler.close()
    handlerErr.close()
    logger.removeHandler(handler)
    logger.removeHandler(handlerErr)
    logger.disabled = True
    

def string_to_dict(cstring, key):
    out = dict()
    try:
        for i in cstring[key].split(';'):
            if '=' in i:
                par = i.split('=')
                out[par[0]] = par[1]
            else:
                out = i
    except:
        raise
    return out

def load_config_file(cfile, cfgdata):
    from io import open
    try:
        with open(cfile, mode='r', encoding='windows-1250') as f:
            output = f.read().splitlines()
    except:
        raise
    for i in range(len(output)):
        key = output[i].rstrip().lstrip().lstrip('##')
        if key in cfgdata:
            cfgdata[key] = output[i + 1]
            cfgdata[key] = string_to_dict(cfgdata, key)
    return cfgdata


def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1", "True", "TRUE")
    

if __name__ == '__main__':
    import lxml
    from lxml import etree
    import uuid
    import requests
    import pytz
    import sys, os
    from datetime import datetime
    cdir = os.getcwd()
    cfile = 'eet_cfg.txt'
    today = datetime.now()
    (logger, handler, handlerErr) = defineLoggers(cfile, today, 'eet_info')
    logger.info('Zahajuji EET, cas: %s' % str(today))
    cfgdata = dict.fromkeys(['url', 'playground', 'production',
                             'directories', 'eet_par', 'payment'])
    try:
        cfgdata = load_config_file(cfile, cfgdata)
    except:
        logger.exception('Nemohu nacist konfiguracni soubor.')
    outdir = cdir + '\\' + cfgdata['directories']['out_dir']
    eetpaths = [cdir + '\\' + cfgdata['directories']['eet_dir'],
                     cdir + '\\' + cfgdata['directories']['cert_dir']]
    [sys.path.append(p) for p in eetpaths
     if os.path.exists(p) and p not in sys.path]
#    sys.path.append('D:\Apps\EET\eet')
    import eet


    prod_url = cfgdata['url']['prod']
    pg_url = cfgdata['url']['pg']
    
    if cfgdata['eet_par']['env'] == 'pg':
        CERT_PATH = (cfgdata['directories']['cert_dir'] + '/' +
                     cfgdata['playground']['cert'])
        CERT_PASS = cfgdata['playground']['pass']
        logger.info('Prostredi: playground. Url: %s' % pg_url)
    elif cfgdata['eet_par']['env'] == 'prod':
        CERT_PATH = (cfgdata['directories']['cert_dir'] + '/' +
                     cfgdata['production']['cert'])
        CERT_PASS = cfgdata['production']['pass']
        logger.info('Prostredi: produkce. Url: %s' % prod_url)
    pokladna = cfgdata['eet_par']['pokladna']
    provozovna = int(cfgdata['eet_par']['provozovna'])
    payment_ID = cfgdata['payment']['id']
    test_fl = str2bool(cfgdata['eet_par']['test_fl'])
    amount = float(cfgdata['payment']['amount'])
    dph_rate = float(cfgdata['eet_par']['dph_rate']) / 100
    a_dph = amount * dph_rate
    total_amount = amount + a_dph
    
    logger.info('Pokladna: %s, provozovna: %s'
                % (cfgdata['eet_par']['pokladna'],
                   cfgdata['eet_par']['provozovna']))
    logger.info('Testovaci mod: %s' % test_fl)
    logger.info('Sazba DPH: %s' % dph_rate)
    logger.info('ID_trzby: %s' % cfgdata['payment']['id'])
    print('ID_trzby: %s' % cfgdata['payment']['id'])
    logger.info('Cena bez DPH: %s, vyse DPH: %s' % (amount, a_dph))
    logger.info('Celkova cena s DPH: %s' % total_amount)
    print('Celkova cena s DPH: %s' % total_amount)
    eet_client = eet.EET(CERT_PATH, CERT_PASS, outdir, provozovna,
                         pokladna=pokladna, eet_url=prod_url)
    payment = eet_client.create_payment(payment_ID, total_amount, test=test_fl)
    payment.set_amount(eet.TAX_BASIC, amount, a_dph)
    result = eet_client.send_payment(payment)
    print (result['fik'])
    logger.info('Kod fik: %s' %result['fik'])
    closeLoggers(logger, handler, handlerErr)