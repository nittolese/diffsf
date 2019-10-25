## Cron Jobs Example

```bash
#If you want to crawl www.test.com every monday at midnight
0 0 * * 1 . $HOME/diffsf_test/sendgrid.env && cd $HOME/diffsf_test/ && python3 worker.py crawl "https://www.test.com" && python3 diff.py

#If you want to crawl www.test.com every day at midnight:
0 0 * * * . $HOME/diffsf_test/sendgrid.env && cd $HOME/diffsf_test/ && python3 worker.py crawl "https://www.test.com" && python3 diff.py

```