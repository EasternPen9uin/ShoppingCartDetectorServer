import datetime, os
from rest_framework.decorators import api_view
from custom_util.custom_utils import CustomResponse
from yolo.models import PictureData
from yolo.models import BoundingBox
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from custom_util.custom_utils import deletePic

# 사진의 id를 받아서 해당 사진의 검출결과 및 파일 경로 확인
@api_view(['POST'])
def getPic(request):
    # 로그인 안 되어 있다면 에러
    if not request.user.is_authenticated:
        return CustomResponse(401, {'detail' : "로그인되어있지 않음" })
    # superuser 아니면 오류
    if not request.user.is_superuser:
        return CustomResponse(403, {"detail" : "잘못된 접근입니다."})

    # id 없으면 오류
    id = request.data.get("id")
    if None in (id, ):
        return CustomResponse(
            400, 
            {"detail" : "요청 형식이 잘못되었습니다."}
        )

    pic_data = None
    try:
        pic_data = PictureData.objects.get(id=id)
    except:
        return CustomResponse(
            404, 
            {"detail" : "존재하지 않는 사진"}
        )

    # 유저 이름 검출    
    username_of_pic = pic_data.user.username

    # 시간 및 폴더 이름 검출
    date = pic_data.date
    folder_name = "%04d%02d%02d" % (date.year, date.month, date.day)
    str_date_time = "%04d-%02d-%02d %02d:%02d:%02d" % (date.year, date.month, date.day, date.hour, date.minute, date.second)

    # 파일 이름 검출(확장자 붙음)
    filename = pic_data.filename

    bounding_boxes = BoundingBox.objects.filter(picture=pic_data)
    ret_bounding_boxes = []
    for box in bounding_boxes:
        new_list = [ box.id, box.xmin, box.ymin, box.xmax, box.ymax ]
        ret_bounding_boxes.append(new_list)
    
    return CustomResponse(
        200,
        {
            "detail" : "success",
            "username" : username_of_pic,
            "date" : str_date_time,
            "nowPath" : "/images/"+folder_name+"/"+filename,
            "nowBoundingBox" : ret_bounding_boxes
        }
    )

# 사진의 id, username를 받아서 
# 해당 사진의 다음 순서에 있는 사진(해당 사진을 찍은 user가 찍은 다음 사진)의 
# 검출결과 및 정보, 다음 사진의 id 확인
@api_view(['POST'])
def getNextPic(request):
    # 로그인 안 되어 있다면 에러
    if not request.user.is_authenticated:
        return CustomResponse(401, {'detail' : "로그인되어있지 않음" })
    # superuser 아니면 오류
    if not request.user.is_superuser:
        return CustomResponse(403, {"detail" : "잘못된 접근입니다."})

    # id 없으면 오류
    id = request.data.get("id")
    if None in (id, ):
        return CustomResponse(
            400, 
            {"detail" : "요청 형식이 잘못되었습니다."}
        )

    pic_data = None
    try:
        pic_data = PictureData.objects.get(id=id)
    except:
        return CustomResponse(
            404, 
            {"detail" : "존재하지 않는 사진"}
        )

    # 유저 및 유저 이름 검출    
    user = pic_data.user
    username_of_pic = pic_data.user.username

    ############################################################
    # 다음 사진 확인
    # 이 지점에서 pic_data가 다음 사진의 pic_data로 바뀌니 주의
    pic_data = None
    # 다음 사진 불러오기
    pic_data = PictureData.objects.filter(user=user, id__gt=id).order_by('id').first()
    if pic_data==None:
        return CustomResponse(
            404, 
            {"detail" : "다음 사진이 없음"}
        )

    # 다음 사진의 id
    new_id = pic_data.id

    # 시간 및 폴더 이름 검출
    date = pic_data.date
    folder_name = "%04d%02d%02d" % (date.year, date.month, date.day)
    str_date_time = "%04d-%02d-%02d %02d:%02d:%02d" % (date.year, date.month, date.day, date.hour, date.minute, date.second)

    # 파일 이름 검출(확장자 붙음)
    filename = pic_data.filename

    bounding_boxes = BoundingBox.objects.filter(picture=pic_data)
    ret_bounding_boxes = []
    for box in bounding_boxes:
        new_list = [ box.id, box.xmin, box.ymin, box.xmax, box.ymax ]
        ret_bounding_boxes.append(new_list)
    
    return CustomResponse(
        200,
        {
            "detail" : "success",
            "nextId" : new_id,
            "username" : username_of_pic,
            "date" : str_date_time,
            "nextPath" : "/images/"+folder_name+"/"+filename,
            "nextBoundingBox" : ret_bounding_boxes
        }
    )

# 사진의 id를 받아서 
# 해당 사진의 이전 순서에 있는 사진(해당 사진을 찍은 user가 찍은 이전 사진)의 
# 검출결과 및 정보, 다음 사진의 id 확인
@api_view(['POST'])
def getPrevPic(request):
    # 로그인 안 되어 있다면 에러
    if not request.user.is_authenticated:
        return CustomResponse(401, {'detail' : "로그인되어있지 않음" })
    # superuser 아니면 오류
    if not request.user.is_superuser:
        return CustomResponse(403, {"detail" : "잘못된 접근입니다."})

    # id 없으면 오류
    id = request.data.get("id")
    if None in (id, ):
        return CustomResponse(
            400, 
            {"detail" : "요청 형식이 잘못되었습니다."}
        )

    pic_data = None
    try:
        pic_data = PictureData.objects.get(id=id)
    except:
        return CustomResponse(
            404, 
            {"detail" : "존재하지 않는 사진"}
        )

    # 유저 및 유저 이름 검출    
    user = pic_data.user
    username_of_pic = pic_data.user.username

    ############################################################
    # 이전 사진 확인
    # 이 지점에서 pic_data가 이전 사진의 pic_data로 바뀌니 주의
    pic_data = None
    # 바로 이전 사진 불러오기
    pic_data = PictureData.objects.filter(user=user, id__lt=id).order_by('-id').first()
    if pic_data==None:
        return CustomResponse(
            404, 
            {"detail" : "이전 사진이 없음"}
        )

    # 이전 사진의 id
    new_id = pic_data.id

    # 시간 및 폴더 이름 검출
    date = pic_data.date
    folder_name = "%04d%02d%02d" % (date.year, date.month, date.day)
    str_date_time = "%04d-%02d-%02d %02d:%02d:%02d" % (date.year, date.month, date.day, date.hour, date.minute, date.second)

    # 파일 이름 검출(확장자 붙음)
    filename = pic_data.filename

    bounding_boxes = BoundingBox.objects.filter(picture=pic_data)
    ret_bounding_boxes = []
    for box in bounding_boxes:
        new_list = [ box.id, box.xmin, box.ymin, box.xmax, box.ymax ]
        ret_bounding_boxes.append(new_list)
    
    return CustomResponse(
        200,
        {
            "detail" : "success",
            "prevId" : new_id,
            "username" : username_of_pic,
            "date" : str_date_time,
            "prevPath" : "/images/"+folder_name+"/"+filename,
            "prevBoundingBox" : ret_bounding_boxes
        }
    ) 

@api_view(['POST'])
def searchPage(request):
    # 로그인 안 되어 있다면 에러
    if not request.user.is_authenticated:
        return CustomResponse(401, {'detail' : "로그인되어있지 않음" })
    # superuser 아니면 오류
    if not request.user.is_superuser:
        return CustomResponse(403, {"detail" : "잘못된 접근입니다."})

    # usernames (유저명(문자열)의 리스트)
    # date ('2023-11-15'형식 문자열)
    # timeStart ('00:10:30' 형식 문자열)
    # timeEnd ('21:36:30' 형식 문자열)
    # viewCounts (숫자. 20, 40, 60, 80, 100)
    # index (숫자)
    # minShoppingCart (정수)
    # 위 내용들 모두 없다면 에러
    usernames, date, timeStart, timeEnd, viewCounts, minShoppingCart = (
        None, None, None, None, None, None
    )
    dateStart, dateEnd = (None, None)

    try:
        usernames = request.data.get("usernames")
        date = datetime.datetime.strptime(request.data.get("date"), '%Y-%m-%d')
        timeStart = list(map(int, request.data.get("timeStart").split(":")))
        dateStart = date.replace(hour=timeStart[0], minute=timeStart[1], second=timeStart[2])
        timeEnd = list(map(int, request.data.get("timeEnd").split(":")))
        dateEnd = date.replace(hour=timeEnd[0], minute=timeEnd[1], second=timeEnd[2]) + datetime.timedelta(seconds=1)
        index = request.data.get("index")
        viewCounts = request.data.get("viewCounts")
        minShoppingCart = request.data.get("minShoppingCart")
        if None in (usernames, date, timeStart, timeEnd, viewCounts, minShoppingCart):
            raise ValueError
        if viewCounts not in (10, 20, 30, 40, 50, 60, 70, 80, 90, 100):
            raise ValueError
    except:
        return CustomResponse(
            400, 
            {"detail" : "요청 형식이 잘못되었습니다."}
        )
    #.filter(user=user, id__lt=id).order_by('-id').first()

    user_lists = [User.objects.get(username=name) for name in usernames]
    
    # userIDs에 있는 유저들로부터 온 사진이면서
    # dateStart와 dateEnd사이에 있으면서
    # minShoppingCart보다 검출된 쇼핑카트의 대수가 큰 애들로 filter
    search_lists = PictureData.objects.filter(
        user__in=user_lists,
        date__gte=dateStart,
        date__lt=dateEnd,
        detected_carts__gte=minShoppingCart
    )
    
    # 반환 결과 준비
    responseData = { "detail" : "success" , "results" : []}

    # 페이지네이션 준비
    paginator = Paginator(search_lists, viewCounts)

    # 총 페이지 확인
    responseData['totalIndex'] = paginator.num_pages

    # 정상적인 페이지범위가 아니여도 에러 
    if not (1 <= index <= responseData['totalIndex']) :
        return CustomResponse(
            400, 
            {"detail" : "요청 형식이 잘못되었습니다. (잘못된 페이지 범위)"}
        )
    
    # 쿼리셋 구하기
    queryset = paginator.get_page(index).object_list



    for pic_obj in queryset:
        #사진id, 유저명, 시간, 검출대수 형식의 리스트의 리스트가 results임
        pic_id = pic_obj.id
        pic_username = pic_obj.user.username
        pic_date = pic_obj.date.strftime("%Y-%m-%d %H:%M:%S")
        detected_shoppingcarts = pic_obj.detected_carts 
        tmp = [pic_id, pic_username, pic_date, detected_shoppingcarts]
        responseData['results'].append(tmp)
    
    return CustomResponse(200, responseData)

# 사진 id 받아서 삭제
@api_view(['DELETE'])
def deleteImage(request):
    # 로그인 안 되어 있다면 에러
    if not request.user.is_authenticated:
        return CustomResponse(401, {'detail' : "로그인되어있지 않음" })
    # superuser 아니면 오류
    if not request.user.is_superuser:
        return CustomResponse(403, {"detail" : "잘못된 접근입니다."})
    # 사진 id 없으면 오류
    id = request.data.get("id")
    if None in (id, ):
        return CustomResponse(
            400, 
            {"detail" : "요청 형식이 잘못되었습니다."}
        )
    # id에 해당하는 사진 있는지 확인 후 없으면 에러
    picData = None
    try:
        picData = PictureData.objects.get(id=id)
    except:
        return CustomResponse(
            404, 
            {"detail" : "존재하지 않는 사진"}
        )
    
    # 이전, 이후 사진의 id를 반환하기 위한 부분
    prevPic = PictureData.objects.filter(user=picData.user, id__lt=id).order_by('-id').first()
    nextPic = PictureData.objects.filter(user=picData.user, id__gt=id).order_by('id').first()
    nextPicId = nextPic.id if nextPic != None else None
    prevPicId = prevPic.id if prevPic != None else None

    # 파일 및 DB데이터 삭제
    deletePic(picData)
    return CustomResponse(200, {
        "detail" : "success",
        "nextPicId" : nextPicId,
        "prevPicId" : prevPicId
    })
#############################
# RESTFUL API로 검출하는건 안 해...
'''
# 프론트엔드랑 공유할 이미지 파일 경로
IMAGE_FILE_PATH = "./../ImageFolder" #'C:/ShoppingCartDetectImages'
# 검출 이미지의 최대 크기 (이거보다 더 크면 이 크기만큼 "적당히" 축소시켜서 검출때림)
# 저장하는 이미지는 원본 그대로 저장함
MIN_IMAGE_SIZE = (480, 270) #(640, 360)

print("모델 로딩 중")
# 모델 로딩
model = torch.hub.load(
    'ultralytics/yolov5', 
    'custom', 
    path="custom_util/best.pt"
)
# 모델을 CPU로 돌릴 생각임
model.to(torch.device("cpu"))
# threshold 지정
model.conf = 0.6
print("모델 로딩 끝")


@api_view(['POST'])
def infer_image(request):
    # 로그인 안 되어 있다면 에러
    if not request.user.is_authenticated:
        return CustomResponse(401, {'detail' : "로그인되어있지 않음" })
    
    # post로 보낸 파일은 request.FILES안에 들어감
    image_blob = request.FILES.get('image')

    # 'image'이라는 이름으로 파일 업로드 안했을 경우에는 에러
    if image_blob == None:
        return CustomResponse(400, {'detail' : "파일이 없음" })

    # 저장용 랜덤코드 생성
    random_code = makeRandomCodes()

    # 저장할 PictureData 하나 생성
    picture_data = PictureData()

    # 이거 찍은 user가 누구인지 넣어줌
    picture_data.user = request.user

    # 안 하니까 null일 수 없다 그런 소리하면서 에러나더라...
    picture_data.detected_carts = 0

    # pk를 얻기 위해 일단 저장함. 다시 DB에서 불러올 필요는 없음.
    picture_data.save()

    # 파일 이름 짓는중 ((pk)_랜덤코드.jpeg)
    filename = "%d_%s.jpeg" % (picture_data.id, random_code)    

    # PictureData에도 파일이름 넣어줌
    picture_data.filename = filename

    # auto_now_add=True라서 picture_data생성시에 안에 이미 날짜가 있어요
    d = picture_data.date #datetime.datetime 객체

    # 현재 날짜(20230101형식)를 폴더 이름으로 함
    folder_name = "%04d%02d%02d" % (d.year, d.month, d.day)

    # 파일경로
    path_without_file = IMAGE_FILE_PATH.rstrip('/') + "/" + folder_name
    file_path = path_without_file + "/" + filename
    
    # 해당 파일경로가 존재하지 않는 경로면 만듦
    import os
    if not os.path.exists(path_without_file):
        os.makedirs(path_without_file)

    # POST로 받은 파일 저장함
    with open(file_path, 'wb+') as destination:
        for chunk in image_blob.chunks():
            destination.write(chunk)

    # 응답 준비
    res = {
        "detail" : "success",
        "bounding_boxes" : []
    }

    # 모델이 인식할 수 있는 형태로 불러옴
    img = cv2.imread(file_path)
    #이미지 사이즈 확인, 리사이징(필요하면), 모델 검출
    img_size = img.shape #(height, width, channel)
    size_difference = (MIN_IMAGE_SIZE[0] * MIN_IMAGE_SIZE[1]) / (img_size[1] * img_size[0])
    if size_difference < 1:
        size_difference_rooted = size_difference**0.5
        img = cv2.resize(img, dsize=(int(img_size[1]*size_difference_rooted), int(img_size[0]*size_difference_rooted)))
    
    # 모델 검출
    predicts = model(img)
    results_refine = predicts.pandas().xyxy[0].values
    
    # 검출결과 DB에 저장+res에도 저장
    img_width = img.shape[1]
    img_height = img.shape[0]
    for bbox in results_refine:
        # 0~1사이의 좌표로 변환
        x0 = bbox[0] / img_width
        y0 = bbox[1] / img_height
        x1 = bbox[2] / img_width
        y1 = bbox[3] / img_height
        # 바운딩박스 개체 생성
        bounding_box = BoundingBox()
        # 좌표 저장
        bounding_box.xmin = x0
        bounding_box.xmax = x1
        bounding_box.ymin = y0
        bounding_box.ymax = y1
        # picture fk 지정
        bounding_box.picture = picture_data
        # 확률 저장
        bounding_box.confidence = bbox[-3]
        # 바운딩박스 다시 저장
        bounding_box.save()
        res['bounding_boxes'].append([x0, y0, x1, y1])
    # picturedata의 detected_carts 수정
    picture_data.detected_carts = len(results_refine)
    picture_data.save()
    
    # @@@ 시간 측정용 + 스트레스 테스트용 + 비동기 확인
    #import time
    #print(f"{request.user.username}으로부터 온 추론요청 끝. 현재 시간 : {time.time()}")

    # 끝
    return CustomResponse(200, res)
'''
