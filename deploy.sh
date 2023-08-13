#!/bin/bash

# 리포지토리 경로로 이동
cd /home/ec2-user/./-Web-My-Study-Materials

# 원격 리포지토리에서 변경 사항 가져오기
git fetch

# 로컬과 원격의 차이점 확인
DIFF=$(git diff HEAD origin)

# 차이점이 있다면 변경 사항 적용
if [ "$DIFF" != "" ]
then
    git pull
    # 필요한 경우 서비스 재시작 등의 명령어 추가
    systemctl restart nginx
fi
