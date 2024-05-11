import speech_recognition as sr
#import sys #-- 텍스트 저장시 사용

r = sr.Recognizer()
kr_audio = sr.AudioFile('C:/KUPepper/pepper/tmp_files/test_file.wav')#음성파일 경로

with kr_audio as source:
    audio = r.record(source)

#sys.stdout = open('news_out.txt', 'w') #-- 텍스트 저장시 사용
print(r.recognize_google(audio, language='ko-KR')) #-- 한글 언어 사용  -> 이부분 client로 넣으먄 댐

#sys.stdout.close() #-- 텍스트 저장시 사용