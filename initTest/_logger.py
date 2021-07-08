import logging
import datetime
import os

def make_logger(name=None):

    dir_path='./saveLog'
    # 0 log를 저장할 폴더가 있는지 체크 없으면 만들어주자
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    # 1 logger instance를 만든다.
    logger = logging.getLogger(name)

    # 2 logger의 level을 가장 낮은 수준인 DEBUG로 설정해둔다.
    logger.setLevel(logging.DEBUG)

    # 3 formatter 지정
    logtime=datetime.datetime.now()
    logtime=str(logtime).replace(":","-") # 파일이름에 ':' 사용불가
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # 4 handler instance 생성

    # 핸들러 생성
    #file_handler = logging.handlers.TimedRotatingFileHandler(
    #    filename=LOG_FILENAME, when='midnight', interval=1, encoding='utf-8'
    #)  # 자정마다 한 번씩 로테이션
    #file_handler.suffix = 'log-%Y%m%d'  # 로그 파일명 날짜 기록 부분 포맷 지정

    console = logging.StreamHandler()
    file_handler = logging.FileHandler(filename=(f"{dir_path}\\{logtime[:-3]}.log"))

    # 5 handler 별로 다른 level 설정
    console.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    # 6 handler 출력 format 지정
    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 7 logger에 handler 추가
    logger.addHandler(console)
    logger.addHandler(file_handler)

    return logger