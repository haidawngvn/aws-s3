from fastapi import APIRouter, File, UploadFile
from utils.S3_baongay import S3_baongay
from typing import List
from utils.schemas import *
from decouple import config

router = APIRouter(
    prefix="",
    tags=["APIS"],
    responses={404: {"description": "Not found"}},
    # dependencies=[Depends(JWTBearer())],
)


@router.post('/upload_single', summary='upload không public')
async def upload(file: UploadFile = File(...)):
    """
    +FILE (str): file cần upload
    """
    s3 = S3_baongay()
    result = s3.upload_file(
        file = file, 
        bucket_name = config('BUCKET_NAME'),
        public_access=False
    )
    return result


@router.post('/get_presigned_url', summary='Lấy presigned url')
async def get_presigned(list: List[presigned_schema]):
    """
    +file_name (str): tên file cần lấy\n
    +size (str | nullable): nếu là ảnh thì truyền vô, accepted values: 'PC' / 'MOBILE'\n
    +expires_time (int | nullable): số second url có hiệu lực, default 60 seconds\n
    """
    s3 = S3_baongay()
    output = []
    for obj in list:
        result = s3.get_presigned_url(file_slug=obj.file_name, expire_time=obj.expire_time, size=obj.size)
        output.append(result)
    return output



        