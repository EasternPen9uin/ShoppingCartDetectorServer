import json
import torch, cv2
from yolo.models import PictureData, BoundingBox
from channels.generic.websocket import AsyncWebsocketConsumer

# 프론트엔드랑 공유할 이미지 파일 경로
from SCD_Backend.settings import MEDIA_URL
IMAGE_FILE_PATH = MEDIA_URL # MEDIA_URL : settings.py에 지정된 경로
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
# 주석 해제시 CPU로 모델이 돌아감
#model.to(torch.device("cpu"))
# threshold 지정
model.conf = 0.7
print("모델 로딩 끝")

# 경보기 API (웹소켓ver)
class MyConsumer(AsyncWebsocketConsumer): 
    # 웹소켓 연결시 실행
    async def connect(self): 
        # 유저 객체 획득 후 권한 확인
        self.user = self.scope["user"]
        
        # 권한 : 로그인 되어있음 + 슈퍼유저 아님
        condition = self.user.is_authenticated and (not self.user.is_superuser)
        # 권한 충족 안되었다면 연결 끊음
        if not condition: 
            await self.send(
                text_data=json.dumps({'message': '권한 없음'})
            )
            await self.close()

        await self.accept()

    # 웹소켓 연결 끊기면 실행
    async def disconnect(self, code):
        return await super().disconnect(code)

    # 브라우저로부터 메시지 받으면 실행
    async def receive(self, text_data=None, bytes_data=None):
        
        # 이미지 안 날아왔다면 종료
        if not bytes_data:
            await self.send(
                text_data=json.dumps({'message': 'Image not found!'})
            )
            await self.close()

        # 생성할 파일 이름을 uuid4로 랜덤하게 생성
        import uuid
        filename = str(uuid.uuid4())+'.jpg'

        # 저장할 PictureData 하나 생성
        picture_data = PictureData()

        # 이거 찍은 user가 누구인지 넣어줌
        picture_data.user = self.user
        
        # 웹소켓 테스트시에 썼던 부분
        #picture_data.user = None

        # 안 하니까 null일 수 없다 그런 소리하면서 에러나더라...
        picture_data.detected_carts = 0

        # PictureData에도 파일이름 넣어줌
        picture_data.filename = filename

        # 날짜정보를 얻기 위해 + 외래키 설정 위해 일단 저장함. 다시 DB에서 불러올 필요는 없음.
        picture_data.save()

        # auto_now_add=True라서 picture_data생성시에 안에 이미 날짜가 있어요
        d = picture_data.date #datetime.datetime 객체

        # 현재 날짜(20230101형식)를 폴더 이름으로 함
        folder_name = "%04d%02d%02d" % (d.year, d.month, d.day)

        path_without_file = IMAGE_FILE_PATH.rstrip('/') + "/" + folder_name
        file_path = path_without_file + "/" + filename

        # 해당 파일경로가 존재하지 않는 경로면 만듦
        import os
        if not os.path.exists(path_without_file):
            os.makedirs(path_without_file) 

        # 날아온 이미지 정보를 저장
        with open(file_path, 'wb') as f:
            f.write(bytes_data)

        # 응답 준비
        res = {
            "message" : "success",
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

        await self.send(
            text_data=json.dumps(res)
        )
        
        # JMeter로 테스트할 때 binary로 반환해야해서 잠시 쓴 부분
        #await self.send(
        #    bytes_data="success!".encode()
        #)