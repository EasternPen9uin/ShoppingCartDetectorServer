# ShoppingCartDetectorServer
2023년도 한양대학교 '인문학기반디지털콘텐츠구축을위한캡스톤디자인' 팀프로젝트의 일환으로 제작된 쇼핑카트 경보기의 백엔드 및 프론트엔드 소스코드입니다.  
Yolov5모델(SCD_Backend/custom_util/best.pt)을 사용하여 쇼핑카트가 검출될 경우 경보를 울리고, 해당 부분의 사진을 저장합니다.  
프론트엔드 폴더의 설정 파일 및 코드는 nginx에서 동작합니다.  
백엔드는 python의 djangorestframework를 사용하며, 백엔드 서버로는 daphne, waitress를 사용합니다.  
DB는 mariaDB를 사용합니다.  

## 서버 실행 전 설정해야 하는 것들
1. 아래 명령어로 파이썬 라이브러리를 설치해주세요.  
```pip install -r requirements.txt```  
2. SCD_Backend/SCD_Backend/settings.py파일의 DATABASES부분의 'USER', 'PASSWORD' 부분에 mariaDB의 유저명과 패스워드를 작성해주세요.  
3. SCD_Backend/SCD_Backend/settings.py파일 내 SECRET_KEY 부분을 반드시 작성해주세요. 아래 링크에서 생성된 것으로 해도 됩니다.  
```https://miniwebtool.com/django-secret-key-generator/```
4. DB에 "shoppingcart_detect"라는 이름의 데이터베이스를 생성합니다. 2번에서 NAME부분을 변경했다면 변경한 이름으로 만듭니다.  
5. 아래 명령어를 사용하여 DB에 스키마를 추가합니다.  
```cd SCD_Backend```  
```python manage.py makemigrations yolo```  
```python manage.py migrate```  
6. 아래 명령어를 사용하여 관리자 계정을 하나 만듭니다.  
```python manage.py createsuperuser```  
7. SCD_FrontEnd_nginx 폴더 내 파일들은 nginx설정파일입니다. nginx를 다운받은 후, SCD_FrontEnd_nginx로 옮기되 중복되는 파일은 겹치지 않도록 합니다.  
8. SCD_FrontEnd_nginx 내 cert폴더를 생성하고, 그 폴더 내에 https연결을 위한 인증서 파일(cert.pem, privKey.pem)을 생성해야합니다.  
* 프론트엔드 코드 중, 카메라에 접근하는 api가 https연결을 요구하므로, 반드시 필요합니다.
## 실행
### 백엔드(SCD_Backend폴더에서)
```waitress-serve --listen=*:8000 SCD_Backend.wsgi:application```
```daphne -b 0.0.0.0 -p 8001 SCD_Backend.asgi:application```
```daphne -b 0.0.0.0 -p 8002 SCD_Backend.asgi:application```
```daphne -b 0.0.0.0 -p 8003 SCD_Backend.asgi:application```
### 프론트엔드(SCD_FrontEnd_nginx폴더에서)
```nginx```

## 접속
서버 실행 후 브라우저에서 IP로 접속 (포트번호 미기입 혹은 443포트로 접속)

## 기타
이 레포지토리는 아래 링크의 2023년도 1학기 AI+X:딥러닝 강의의 팀프로젝트의 연장선으로 진행된 프로젝트입니다.  
https://github.com/EasternPen9uin/ShoppingCartDetector  
이 레포지토리에 사용된 모델은 2023년도 1학기의 데이터셋에서 이마트 쇼핑카트 데이터셋을 직접 촬영하여 보완한 모델입니다.  