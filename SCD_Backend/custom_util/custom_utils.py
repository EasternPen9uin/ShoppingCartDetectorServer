from rest_framework.response import Response
import os

def CustomResponse(status_code : int, response_without_code):
    response_without_code['status_code'] = status_code
    return Response(response_without_code, status=status_code)

# picture 엔티티 하나 받아서 파일 삭제 후 DB에서도 삭제
def deletePic(pic_data) :
    deleteShoppingCartImageFile(pic_data.filename, pic_data.date)
    # DB도 삭제(boundingBox 정보는 CASCADE이므로 django가 알아서 삭제해줌)
    pic_data.delete()

# 파일 이름(확장자 포함)과 datetime객체 받아서 해당하는 사진 및 폴더 삭제 
def deleteShoppingCartImageFile(filename, date):
    # 프론트엔드랑 공유할 이미지 파일 경로
    from SCD_Backend.settings import MEDIA_URL
    IMAGE_FILE_PATH = MEDIA_URL # MEDIA_URL : settings.py에 지정된 경로
    # 폴더 경로와 파일 경로 구함
    pic_folderpath = IMAGE_FILE_PATH.rstrip('/') + "/" + date.strftime("%Y%m%d")
    pic_filepath = pic_folderpath + '/' + filename
    # 실물 파일은 삭제
    if os.path.isfile(pic_filepath):
        os.remove(pic_filepath)
    else:
        print(f"경고 : 존재하지 않는 파일({pic_filepath})")
    if os.path.exists(pic_folderpath):
        # 파일 삭제 후 더 이상 해당 날짜 폴더에 사진이 없다면 해당 폴더도 삭제
        if not list(filter(lambda x : (x.endswith(".jpg")), os.listdir(pic_folderpath))):
            os.rmdir(pic_folderpath)
    else:
        print(f"경고 : 존재하지 않는 폴더({pic_folderpath})")



def isValidUsername(arg_username):
    import re
    username_regex = re.compile(r'^[a-zA-Z0-9_]{3,20}$')
    return bool(username_regex.match(arg_username))

def isValidPassword(arg_password):
    import re
    password_regex = re.compile(r'^(?=.*[a-zA-Z])(?=.*[!@#$%^*+=_-])(?=.*[0-9])[a-zA-Z0-9!@#$%^*+=_-]{7,30}$')
    return bool(password_regex.match(arg_password))