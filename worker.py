# -*- coding: utf-8 -*-
usage='''
👾 Automated Screaming Frog Worker

🔍 Usage:
    worker.py crawl <site>
    worker.py (-h | --help)

💡 Examples:
    ▶️  worker.py crawl "https://searchon.it/"
    ▶️  worker.py crawl "https://searchon.it/" config "some.seospiderconfig"
    ▶️  worker.py -h                              Print this message
   
👀 Options:
    -h, --help

'''

from datetime import date, timedelta
import subprocess
from docopt import docopt

args = docopt(usage)
today = date.today()

cmd = 'screamingfrogseospider --crawl ' + args['<site>'] + ' --headless --config testconfig.seospiderconfig --export-tabs "Internal:All"'
cmd += f" && mv internal_all.csv internal_all_{today.day}{today.month}{today.year}.csv"
try:
    proc = subprocess.run(cmd, shell=True)
except subprocess.CalledProcessError:
    print('[SF] Exception raised while running Screaming Frog')
