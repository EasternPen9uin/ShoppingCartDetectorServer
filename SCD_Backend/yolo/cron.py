import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.combining import OrTrigger
from yolo.models import PictureData
from custom_util.custom_utils import deleteShoppingCartImageFile

# 매일 09시, 22시에 15일 이상 경과한 사진의 DB정보, 검출정보, 파일 삭제
def job():
    # 삭제 기준
    from SCD_Backend.settings import MAXIMUM_PHOTO_STORAGE_DURATION
    delete_criteria = datetime.datetime.now() - datetime.timedelta(days = MAXIMUM_PHOTO_STORAGE_DURATION)
    # 미리 삭제할 사진들 정보를 받아옴
    pics = PictureData.objects.filter(date__lt=delete_criteria)
    filename_folder_tuples = []
    for onePic in pics:
        filename_folder_tuples.append((onePic.filename, onePic.date))    
    # DB에서 삭제
    PictureData.objects.filter(date__lt=delete_criteria).delete()
    # 파일 시스템 상에서도 삭제
    for filename, date in filename_folder_tuples:
        deleteShoppingCartImageFile(filename, date)

def main():
    sched = BackgroundScheduler()
    trigger = OrTrigger([CronTrigger(hour=9), CronTrigger(hour=22)])
    sched.add_job(job, trigger=trigger, id='autoDelete')
    sched.start()
