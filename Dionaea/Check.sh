#!/bin/bash
# Author: atiger77
# Date: 2016/08/11
# Version: V1.3
# Desc: This script will check Dionaea.log's md5.
#       Rember add this  script to crontab.
#       */5 * * * * /bin/bash /xxx(script-location)/Check.sh

# Define
Log_location="/tmp/Dionaea.log"
Check_MD5_location="/tmp/dionaea_md5check.txt"
Alarm_Email="yyy@xxx.com"
Dionaea_Hostname=`hostname`
# Try to get IP more robustly
Dionaea_HostIP=`hostname -I | awk '{print $1}'`


# Check MD5 file.
if [ ! -s $Check_MD5_location ]; then
    echo `/usr/bin/md5sum $Log_location` > $Check_MD5_location
fi


# Contrast file.
Old_md5=`awk '{print $1}' $Check_MD5_location`
New_md5=`/usr/bin/md5sum $Log_location | awk '{print $1}'`
if [ "$Old_md5" == "$New_md5" ]; then
    sleep 0.5
else
    /usr/bin/md5sum $Log_location > $Check_MD5_location
    
    # 1. Send Email Alert
    echo -e "Dionaea logs changed!!! Please check: \nhostname:$Dionaea_Hostname hostip:$Dionaea_HostIP" | mailx -s "Web_Dionaea logs was changed!" $Alarm_Email 
    
    # 2. Trigger Login Statistics
    /bin/bash /home/kali/Dionaea/Dinonaea-web/Dionaea/Login_statistics.sh
    
    # 3. Notify Backend to Refresh Stats (Using Python script to bypass HTTP Auth)
    cd /home/kali/Dionaea/Dinonaea-web/Dionaea
    source backend/venv/bin/activate
    PYTHONPATH=backend python backend/scripts/refresh_cache.py
fi
