#!/bin/bash

# 리포지토리 경로로 이동
cd /home/ec2-user/-Web-My-Study-Materials

# 원격 리포지토리에서 변경 사항 가져오기
git fetch

# 로컬과 원격의 차이점 확인
DIFF=$(git diff HEAD origin)

if [ "$DIFF" != "" ]
then
    git pull
    echo "$(date) : Git pulled successfully" >> /var/log/my_cron.log # 로그에 기록
    # 필요한 경우 서비스 재시작 등의 명령어 추가
    systemctl restart nginx
    echo "$(date) : Nginx restarted" >> /var/log/my_cron.log # 로그에 기록
fi