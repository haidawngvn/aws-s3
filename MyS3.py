import boto3
import os
import shutil

class MyS3():
    
    # content_type sẽ hỗ trợ show image trong browser,
    # còn word, excel sẽ buộc download
    content_types = {
        'word': 'application/msword',
        'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'image': 'image/jpeg'
    }
    
    def __init__(self):
        self.__s3 = boto3.resource('s3')
            
    def get_bucket(self, bucket_name):
        for bucket in self.__s3.buckets.all():
            # print(bucket.name)
            if bucket.name == bucket_name:
                my_bucket = self.__s3.Bucket(bucket.name)
                return my_bucket
        return False
    
    
    def upload_file(self, upload_file, bucket_name, location, public_access):
        '''
        upload_file (File): path dẫn tới file cần upload
        bucket_name (str): tên bucket
        key (str): location muốn lưu trong bucket (mặc định ở root của bucket)
        '''
        if location != '' and location[-1] != '/':
            location += '/'

        # Xét xem file có dc hỗ trợ không 
        file_type = self.get_file_type(upload_file.filename)
        if not file_type:
            return 'Định dạng file không hỗ trợ'

        extra_args = {
            'ContentType': self.content_types[file_type]
        }
        if public_access:
            extra_args['ACL'] = 'public-read'
            
        try:
            self.write_file(upload_file)
            self.__s3.meta.client.upload_file(
                upload_file.filename, 
                bucket_name, 
                location+upload_file.filename,
                ExtraArgs=extra_args
            )
            return {
                'host': 'https://haidawng-bucket-1.s3.ap-northeast-1.amazonaws.com/',
                'filename': location+upload_file.filename,
                'path': f'https://haidawng-bucket-1.s3.ap-northeast-1.amazonaws.com/{location+upload_file.filename}',
            }
        except Exception:
            print('Somewhere went wrong :D')
            return 'Somewhere went wrong :D'
        finally:
            print('Xóa file')
            self.delete_file(upload_file.filename)
        
    def clear_bucket(self, bucket_name):
        bucket = self.get_bucket(bucket_name)
        if bucket:
            try:
                for key in bucket.objects.all():
                    key.delete()
                return True
            except Exception:
                return False
        return False
    
    def remove_file(self, bucket_name, file_name, file_location):
        if file_location != '' and file_location[-1] != '/':
            file_location += '/'
        key = file_location+file_name
        try:
            self.__s3.meta.client.delete_object(Bucket=bucket_name, Key=key)
            return 'Xóa thành công'
        except Exception:
            return 'Đã xảy ra lỗi :P'
    
    def get_presigned_url(self, bucket, key, expires_time=60):
        url = boto3.client('s3').generate_presigned_url(
            ClientMethod='get_object', 
            Params={
                'Bucket': bucket, 
                'Key': key
            },
            ExpiresIn=expires_time #second
        )
        return url

    def download_file(self, bucket_name, file, download_location):
        boto3.client('s3').download_file(bucket_name, file, download_location)
        # pass
    
    
    def write_file(self, file):
        with open(f'{file.filename}', 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
    
    def delete_file(self, filename):
        os.remove(filename)

    def get_file_type(self, filename):
        """
            Trả về file type của file name
            Nếu file không dược hỗ trợ sẽ trả về False
        """
        file_name = filename
        if '/' in filename:
            file_name = filename.split('/')[-1]
        elif '\\' in filename:
            file_name = filename.split('\\')[-1]
        
        file_extension = file_name.split('.')[-1]

        # allowed_file_types = ['doc', 'docx', 'xls', 'xlsx', 'jpeg', 'jpg', 'png', 'PNG']
        
        if file_extension == 'doc' or file_extension == 'docx':
            return 'word'
        elif file_extension == 'xls' or file_extension == 'xlsx':
            return 'excel'
        elif file_extension == 'jpeg' or file_extension == 'png' or file_extension == 'jpg' or file_extension == 'PNG':
            return 'image'
        else:
            return False