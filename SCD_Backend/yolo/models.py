from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class PictureData(models.Model):
    # 식별번호용
    id = models.BigAutoField(primary_key=True) #PK, serial
    # 사진 누가 올렸는지. 
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # 올린 날짜
    date = models.DateTimeField(auto_now_add=True)
    # 파일 이름
    filename = models.CharField(max_length=150)
    # 검출된 카트 갯수
    detected_carts = models.IntegerField()

class BoundingBox(models.Model):
    # 식별번호용
    id = models.BigAutoField(primary_key=True) #PK, serial
    # PictureData에 대한 외래키
    # CASCADE : 사진 자체가 날아갔다면 검출 결과도 같이 삭제함
    picture = models.ForeignKey(PictureData, on_delete=models.CASCADE) 
    # xmin
    xmin = models.FloatField()
    # ymin
    ymin = models.FloatField()
    # xmax
    xmax = models.FloatField()
    # ymax
    ymax = models.FloatField()
    # confidence
    confidence = models.FloatField()