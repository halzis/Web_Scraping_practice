from tkinter import *
from tkinter import messagebox
from tkinter import ttk
import requests
import csv
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from webbrowser import open as web_open
from math import ceil
from bs4 import BeautifulSoup
from functools import partial

class data:
    key = ""
    jobkorea_jobs = []
    last = []

    def __add__(self,other):
        j = self.jobkorea_jobs + other.jobkorea_jobs
        return j

d = data()

def first_win():
    global d
    # 마지막 페이지, 마지막 페이지의 공고 갯수, 전체 공고 갯수 반환하는 함수
    def get_last(URL):
        # requests의 모듈을 이용해 검색한 페이지의 정보를 가져와
        # html을 분석하기 위해 BeautifulSoup 객체 생성
        result = requests.get(URL)
        data = BeautifulSoup(result.text,"html.parser")
        # 공고의 전체 갯수가 들어있는 html의 class 불러옴
        notice_count = data.find("strong", {"class":"dev_tot"}).string

        count_str = []
        count_int = 0
        last_page = 0
        last_page_count = 0

        # 전체 갯수에 있는 ',' 제거
        for x in notice_count:
            if x != ',':
                count_str.append(x)
        # 문자열로 되어있는 전체 갯수를 정수형으로 바꿈
        for x in count_str:
            count_int = count_int*10+int(x)
        # 한 페이지당 20개의 공고를 나타내기 때문에 20으로 나눈 후
        # 반올림하여 전체 페이지 수를 계산
        last_page = count_int / 20
        last_page = ceil(last_page)
        last_page_count = count_int % 20
        return last_page,last_page_count,notice_count

    # 각 공고의 정보를 반환하는 함수
    def job_data(job):
        # 회사 이름은 잡코리아의 html 중 a라는 태그 안 title에 저장돼있기 때문에
        # a태그의 title을 찾아서 저장
        company = job.find("a")["title"]
        # 공고 이름은 div 태그의 post-list-info라는 클래스 안에 있음
        title = job.find("div",{"class":"post-list-info"}).find("a")["title"]
        # 지역은 loc long이라는 클래스가 있는 span 태그의 내용
        location = job.find("span",{"class":"loc long"}).string
        # 경력은 exp라는 클래스가 있는 span 태그의 내용
        exp = job.find("span",{"class":"exp"}).string
        # 학력이 적혀있지 않다면 공백 저장, 적혀있다면 내용 저장
        if job.find("span",{"class":"edu"}) == None:
            edu = ""
        else:
            edu = job.find("span",{"class":"edu"}).string
        # 공고를 보기위한 공고번호만 가져오기 위해
        # 공고번호 왼쪽과 오른쪽을 지움
        notice_num = job.find("a")["href"]
        notice_num = notice_num.lstrip("/Recruit/GI_Read/")
        notice_num = notice_num.rstrip("?Oem_Code=C1&amp;logpath=1")
        # 딕셔너리 반환
        return {
        "제목":title,
        "회사":company,
        "경력":exp,
        "학력":edu,
        "지역":location,
        "공고보기":f"http://www.jobkorea.co.kr/Recruit/GI_Read/{notice_num}"}

    # 모든 페이지의 모든 공고 정보를 반환하는 함수
    def collect_job(URL,last_page,last_page_count,all_count):
        jobs = []    # 모든 공고의 정보를 저장할 리스트
        # 1페이지부터 마지막페이지까지 반복
        for page in range(1,last_page+1):
            # 현재 페이지의 정보를 가져옴
            result = requests.get(f"{URL}&Page_No={page}")
            page_data = BeautifulSoup(result.text,"html.parser")
            # 현재 페이지의 모든 공고를 가져옴
            all_data = page_data.find_all("li",{"class":"list-post"})
            # 마지막 페이지라면 마지막 페이지에 존재하는 공고 갯수만큼 반복
            if page == last_page:
                for data in all_data[0:last_page_count]:
                    jobs.append(job_data(data))
            # 마지막 페이지가 아니라면 20번 반복(페이지당 20개 공고를 볼 수있음)
            else:
                for data in all_data[0:20]:
                    jobs.append(job_data(data))
        messagebox.showinfo("완료","검색 완료")
        messagebox.showinfo("완료",all_count+"개의 공고가 검색되었습니다.")
        window.destroy()
        return jobs

    def search(t):
        global d
        messagebox.showinfo("알림","렉이 걸려도 가만히 기다리면 됩니다.")
        # 잡코리아의 검색창 URL에 검색 키워드를 넣음
        URL = "http://www.jobkorea.co.kr/Search/?stext="
        t.key = en.get()
        URL = URL+t.key
        t.last = get_last(URL)
        t.jobkorea_jobs = collect_job(URL,t.last[0],t.last[1],t.last[2])
        d.jobkorea_jobs = d + t
        d.key = t.key
        d.last = t.last
        window.quit()

    temp = data()
    # 윈도우 생성 후 타이틀, 창 크기 설정(창 크기 변경불가)
    window = Tk()
    window.title("검색")
    window.geometry("390x190")
    window.resizable(False, False)
    # 레이블, 엔트리(검색창), 검색 버튼 생성 후 위치 설정
    la=Label(window,text = "검색어를 입력하세요.",font="나눔고딕 13")
    la.place(x=120,y=40)

    en = Entry(window,width=30)
    en.place(x=90,y=80)

    bu=Button(window,text="검색",font="나눔고딕 10",width=10,height=2,command= partial(search,temp))
    bu.place(x=145,y=130)

    window.mainloop()

def second_win():
    # 첫 번째 버튼(보기)를 선택했을 때 전체 공고를 표로 보여주는 함수
    def choice1():
        global d
        def save_csv():
            # 엑셀 파일 저장
            file = open("jobkorea_jobs.csv",mode="w",newline="")
            writer = csv.writer(file)
            writer.writerow([d.key])
            writer.writerow(["제목", "회사", "경력", "학력", "지역", "공고보기"])
            for job in d.jobkorea_jobs:
                writer.writerow(list(job.values()))
            messagebox.showinfo("저장","이 프로젝트가 있는 경로에 엑셀 파일이 저장되었습니다.")
        def add_csv():
            # 기존의 엑셀 파일에 내용 추가
            file = open("jobkorea_jobs.csv",mode="a",newline="")
            wr = csv.writer(file)
            wr.writerow("")
            wr.writerow([d.key])
            for job in d.jobkorea_jobs:
                wr.writerow(list(job.values()))
            messagebox.showinfo("추가","csv 파일에 내용이 추가되었습니다.")
        def del_csv():
            # 엑셀 파일이 프로젝트와 같은 폴더에 있다면 삭제
            if os.path.isfile("jobkorea_jobs.csv"):
                os.remove("jobkorea_jobs.csv")
                messagebox.showinfo("삭제","삭제가 완료되었습니다.")
            else:
                messagebox.showerror("에러","파일이 존재하지 않습니다.")
        def research():
            # 다시 검색할 수 있게 창을 열어주는 함수
            select_window.destroy()
            select_window.quit()
            first_win()
            second_win()
        # 공고를 선택하고 공고 보기를 눌렀을 때 공고를 인터넷으로 열어주는 함수
        def choice1_button():
            # 현재 선택한 줄이 몇번째줄인지 문자열 형태로 가져와 앞의 문자를 제거
            item = treeview.focus()
            item = item.lstrip("I00")
            # 16진수형태로 나오기때문에 16진수를 10진수로 변환
            item = "0x"+item
            item = int(item,16)
            # jobkorea_jobs의 링크를 가져오기 위해 global 사용
            #링크 불러와서 webbrowser의 open 함수 사용해 링크 인터넷으로 열어줌
            notice_URL = d.jobkorea_jobs[item-1]["공고보기"]
            web_open(notice_URL)
        # 추가 창 실행
        list_window = Toplevel(select_window)
        list_window.title("리스트 보기")
        list_window.geometry("1000x350")
        list_window.resizable(False,False)

        # 메뉴에 저장, 추가, 삭제, 재검색 추가
        menubar=Menu(list_window)
        f1=Menu(menubar,tearoff=0)
        f1.add_command(label="저장",command=save_csv)
        f1.add_command(label="추가",command=add_csv)
        f1.add_command(label="삭제",command=del_csv)
        f1.add_separator()
        f1.add_command(label="재검색",command=research)
        menubar.add_cascade(label="File",menu=f1)
        list_window.config(menu=menubar)
        # 리스트를 출력할 프레임과 버튼을 출력할 프레임
        frame = Frame(list_window)
        bu_frame = Frame(list_window)
        # 버튼과 스크롤바, 여러 열을 표로 나타내주는 treeview 생성
        button = Button(bu_frame,text="공고보기",font="나눔고딕 10",
        width=10,height=2,command=choice1_button)
        scrollbar=Scrollbar(frame)
        scrollbar.pack(side="right",fill="y")
        treeview = ttk.Treeview(frame,columns=["제목","회사","경력","학력","지역"]
        ,yscrollcommand=scrollbar.set)
        # 첫번째 칸 공백 제거 후 각 열의 첫 줄 작성
        treeview['show'] = 'headings'
        treeview.column("제목",width=450)
        treeview.heading("제목",text="제목")
        treeview.column("회사",width=150)
        treeview.heading("회사",text="회사")
        treeview.column("경력",width=100)
        treeview.heading("경력",text="경력")
        treeview.column("학력",width=100)
        treeview.heading("학력",text="학력")
        treeview.column("지역",width=130)
        treeview.heading("지역",text="지역")
        # 수집한 정보를 treeview에 나타냄
        for i in range(len(d.jobkorea_jobs)):
            treeview.insert('','end',values=(d.jobkorea_jobs[i]["제목"],
            d.jobkorea_jobs[i]["회사"],d.jobkorea_jobs[i]["경력"],
            d.jobkorea_jobs[i]["학력"],d.jobkorea_jobs[i]["지역"]))
        treeview.pack(side="top",pady=10)
        scrollbar["command"]=treeview.yview
        button.pack(side="top",anchor="e",padx=60,pady=10)
        frame.pack()
        bu_frame.pack(fill="both")
        list_window.mainloop()

    def choice2():
        global d
        def find_ID():
            # 아이디 찾기 페이지를 열어주는 함수
            find_URL = "https://accounts.google.com/signin/v2/usernamerecovery?continue=https%3A%2F%2Fmyaccount.google.com%2Fintro%3Futm_source%3DOGB%26tab%3Drk%26utm_medium%3Dapp&csig=AF-SEnbvohL617RKuC81%3A1591145250&hl=ko&service=accountsettings&flowName=GlifWebSignIn&flowEntry=AddSession"
            web_open(find_URL)
        def login():
            # gmail 아이디, 비밀번호를 받음
            ID = ID_entry.get()
            PW = PW_entry.get()
            username = ID.rstrip("@gmail.com")

            # 엑셀 파일 저장
            file = open("jobkorea_jobs.csv",mode="w",newline="")
            writer = csv.writer(file)
            writer.writerow([d.key])
            writer.writerow(["제목", "회사", "경력", "학력", "지역", "공고보기"])
            for job in d.jobkorea_jobs:
                writer.writerow(list(job.values()))

            # 예외 처리
            try:
                # 메일을 보내기 위해 객체를 생성, 보내는 사람과 받는 사람을 자신으로 설정
                msg = MIMEMultipart()
                msg['From'] = ID
                msg['To'] = ID

                # 보낼 파일을 오픈함
                filename = "jobkorea_jobs.csv"
                attachment = open(filename,'rb')

                # 파일을 이진 파일로 불러와 인코딩을 한 후 첨부
                part = MIMEBase('application','octet-stream')
                part.set_payload((attachment).read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition',"attachment; filename= "+filename)
                msg.attach(part)

                # gmail 서버를 불러온 후 로그인하여 메일을 보낸 후 서버를 닫음
                text = msg.as_string()
                server = smtplib.SMTP("smtp.gmail.com",587)
                server.starttls()
                server.login(username,PW)
                server.sendmail(ID,ID,text)
                server.quit()

                # 열었던 파일을 닫고 삭제
                attachment.close()
                file.close()
                os.remove("jobkorea_jobs.csv")
                
                messagebox.showinfo("완료","파일 전송을 완료했습니다.")
            # 에러 발생시 에러메시지 출력
            except smtplib.SMTPAuthenticationError:
                messagebox.showinfo("에러","ID나 비밀번호를 다시 확인하거나 에러 발생을 눌러주세요.")

        def err():
            # 에러 발생시 보안 수준이 낮은 앱 허용 사용 변경
            err_URL = "https://myaccount.google.com/lesssecureapps"
            web_open(err_URL)
            messagebox.showinfo("에러 발생","""로그인 후 '보안 수준이 낮은 앱 허용'을
            사용함으로 변경해주세요.""")

        # gmail 로그인을 위해 윈도우를 하나 더 생성
        login_window = Toplevel(select_window)
        login_window.title("gmail 로그인")
        login_window.geometry("370x190")
        login_window.resizable(False,False)
        notice_label = Label(login_window,text="""gmail만 가능합니다.
        (@gmail.com도 붙여주세요)""",font="나눔고딕 13")
        # 로그인을 위해 Entry와 버튼 생성
        ID_label = Label(login_window, text="ID",font="나눔고딕 10")
        ID_entry = Entry(login_window,width=24)
        PW_label = Label(login_window,text="PW",font="나눔고딕 10")
        PW_entry = Entry(login_window,width=24,show="*")
        login_button = Button(login_window,text="로그인",font="나눔고딕 10",width=8,height=3,command=login)
        ID_button = Button(login_window,text="ID 찾기",font="나눔고딕 10",width=8,height=2,command=find_ID)
        err_button = Button(login_window,text="에러 발생",font="나눔고딕 10",width=8,height=2,command=err)
        notice_label.place(x=60,y=15)
        ID_label.place(x=40,y=65)
        ID_entry.place(x=80,y=65)
        PW_label.place(x=40,y=105)
        PW_entry.place(x=80,y=105)
        login_button.place(x=270,y=65)
        ID_button.place(x=80,y=140)
        err_button.place(x=180,y=140)

    # 검색한 공고들을 그냥 볼지, 엑셀파일로 저장할지, 엑셀파일을 메일로 보낼지 선택하는 창
    select_window = Tk()
    select_window.title("선택")
    select_window.geometry("390x180")
    select_window.resizable(False, False)

    select2 = """엑셀 파일
    메일로 보내기"""

    b1=Button(select_window,text="보기",font="나눔고딕 10",width=17,height=3,command=choice1)
    b1.place(x=40,y=65)

    b2=Button(select_window,text=select2,font="나눔고딕 10",width=17,height=3,command=choice2)
    b2.place(x=220,y=65)

    select_window.mainloop()

first_win()
second_win()