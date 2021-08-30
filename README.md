# kea-bg-monitor
Set up bespoke CGM BG alerts for the Dexcom G6

Read accompanying blog post : https://seshadri.xyz/cgm-alerts-t1d.html

Run `pip3 install -r requirements.txt; python3 monitor.py`

Optionally set the following os env vars: 
```
export TWILIO_ACCOUNT_SID=''
export TWILIO_AUTH_TOKEN=''
export MY_PHONE_NUMBER=''
export TWILIO_PHONE_NUMBER=''
export MY_TIMEZONE='America/Los_Angeles'
```