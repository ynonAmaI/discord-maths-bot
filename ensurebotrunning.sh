#! /bin/bash

case "$(pidof python3.6 | wc -w)" in
0) echo "Restarting Maths Bot:   $(date)" >> maths-bot-restarting-log.txt
   nohup python3.6 /home/USERNAME/maths-bot.py &
   ;;
1) #maths bot is running!
   ;;
*) echo "Removed additional instances of the maths bot:   $(date)" >> maths-bot-restarting-log.txt
   ;;
esac