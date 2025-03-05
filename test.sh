#!/bin/bash
echo "##########################"
echo "###Running CONF tests!####" 
echo "##########################"
echo ""
#Configuration File Automate Testing

# number of conf test cases run so far
count_conf=0 

for test in ~/conf_error_test/*.conf; do
    #Load conf error test cases to Configuration File
    name=$(basename $test .conf)
    cat ~/conf_error_test/$name.conf > ~/.runner.conf
    expected=~/conf_error_test/$name.out

    #Compare runner.py Output with Expected Output
    python3 ~/runner.py | diff - $expected || echo "Test $name: failed!\n"

    count_conf=$((count_conf+1))
done

echo "Finished running $count_conf CONFIGURATION FILE tests!"


echo ""
echo "##########################"
echo "####Running e2e tests!####"
echo "##########################"
echo ""

#Generate suitable date and time for End to End Test
weekday=`/bin/date '+%A'`
last_weekday=`/bin/date -d "1 day ago" '+%A'`
next_weekday=`/bin/date -d tomorrow '+%A'`
time_1=`/bin/date --date 'now + 1 minutes' '+%H%M'`
time_2=`/bin/date --date 'now + 2 minutes' '+%H%M'`
time_3=`/bin/date --date 'now + 3 minutes' '+%H%M'`
time_4=`/bin/date --date 'now + 4 minutes' '+%H%M'`

#Initialise the Configuration File with correct syntax
cat > ~/.runner.conf << EOF
on $weekday at $time_1 run /bin/echo Hello World!
on $weekday at $time_2 run error_file
every $last_weekday,$weekday,$next_weekday at $time_3,$time_4 run /bin/date
EOF

#Manual Testing
python3 ~/runner.py &
sleep 2
echo "##Runstatus Output##"
python3 ~/runstatus.py

#Print runner.py output for Manual Testing
echo "###Runner Output####"
sleep 60
#Print different output of runstatus.py
#between different ouput of runner.py for Manual Testing
echo "##Runstatus Output##"
python3 ~/runstatus.py

echo "###Runner Output####"
sleep 60

echo "##Runstatus Output##"
python3 ~/runstatus.py

echo "###Runner Output####"
sleep 60

echo "##Runstatus Output##"
python3 ~/runstatus.py

echo "###Runner Output####"
sleep 60

echo "##Runstatus Output##"
python3 ~/runstatus.py

sleep 10

#Terminate runner.py Manully
pid=`cat ~/.runner.pid`
kill -9 $pid
echo ""
echo "##########################"
echo "###Finished e2e tests!####"
echo "##########################"


