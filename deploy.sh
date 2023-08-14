#!/bin/bash

# 로그 파일 경로 설정
LOGFILE="/path/to/your/logfile.log"

# 리포지토리 경로로 이동
cd /home/ec2-user/-Web-My-Study-Materials

# 원격 리포지토리에서 변경 사항 가져오기
git fetch

# 로컬과 원격의 차이점 확인
DIFF=$(git diff HEAD origin)

# git pull 후에 gunicorn 재시작
if [ "$DIFF" != "" ]
then
    git pull
    echo "$(date) : Git pulled successfully" >> $LOGFILE
    pkill gunicorn
    # 가상 환경 활성화
    source /home/ec2-user/myenv/bin/activate
    gunicorn --bind 0.0.0.0:8000 my_study_materials.wsgi:application &
    echo "$(date) : Gunicorn restarted" >> $LOGFILE

    sudo systemctl restart nginx
    echo "$(date) : Nginx restarted" >> $LOGFILE
fi