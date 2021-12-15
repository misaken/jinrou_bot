from flask import Flask,request,abort
from linebot import LineBotApi,WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (MessageEvent,TextMessage,TextSendMessage,
                            FollowEvent, TemplateSendMessage, LeaveEvent,
                            CarouselTemplate, PostbackEvent, JoinEvent
                            )
from linebot.models.events import Postback, PostbackEvent
import random, string, os,  time
from Class import button,poll,DB


app=Flask(__name__)
#環境変数の取得
#直打ちは危険なのでosで取得
DATABASE_URL = os.environ['DATABASE_URL']
YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
line_bot_api=LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler=WebhookHandler(YOUR_CHANNEL_SECRET)
db=DB()

def getouhyou(user_id):
    with db:
        cur = db.execute("select id from jinrou where id not in ('{}') and status='alive'". format(user_id))
        rows = cur.fetchall()
        touhyou_id=[]
        for i in rows:
            touhyou_id.append(i[0])
        cur = db.execute("select name from jinrou where id not in ('{}') and status='alive'". format(user_id))
        rows = cur.fetchall()
        touhyou_name=[]
        for i in rows:
            touhyou_name.append(i[0])
        cur = db.execute("select role from jinrou where id not in ('{}') and status='alive'". format(user_id))
        rows = cur.fetchall()
        touhyou_r=[]#一旦DBからrole正しく取得
        for i in rows:
            touhyou_r.append(i[0])
        touhyou_role=[]
        for m in range(len(touhyou_r)):
            if touhyou_r[m] == "人狼":
                touhyou_role.append("人狼")
            elif touhyou_r[m] != "人狼":
                touhyou_role.append("人間")
            else:
                pass
    return touhyou_name,touhyou_role,touhyou_id


def jinrou_touhyou():
    with db:
        cur=db.execute("select name from jinrou where status='alive' and role !='人狼'")
        rows=cur.fetchall()
        jintouhyou=[]
        for i in rows:
            jintouhyou.append(i[0])
    return jintouhyou

def death_note():
    with db:
        cur=db.execute("select name from jinrou where status='death'")
        rows = cur.fetchall()
        deathnotelist_n = []
        #リストの中のコンマを取り除く
        for i in rows:
            deathnotelist_n.append(i[0])
        cur=db.execute("select role from jinrou where status='death'")
        rows = cur.fetchall()
        deathnotelist_r = []
        #リストの中のコンマを取り除く
        for i in rows:
            deathnotelist_r.append(i[0])
    return deathnotelist_n,deathnotelist_r

#生きている人狼のリスト取得
def jinrou_Meibo():
    with db:
        cur=db.execute("select name from jinrou where status='alive' and role='人狼'")
        rows = cur.fetchall()
        jinrou_Meibo_List=[]
        #リストの中のコンマを取り除く
        for i in rows:
            jinrou_Meibo_List.append(i[0])
    return jinrou_Meibo_List

def game():
    global night_count
    idList = []
            #nameList = worksheet.get_name()
    with db:
        cur = db.execute("select id from jinrou")
        rows = cur.fetchall()
        for i in rows:
            idList.append(i[0])
    roleList = []
    #nameList = worksheet.get_name()
    with db:
        cur = db.execute("select role from jinrou")
        rows = cur.fetchall()
        for i in rows:
            roleList.append(i[0])
    statusList = []
    with db:
        cur = db.execute("select status from jinrou")
        rows = cur.fetchall()
        for i in rows:
            statusList.append(i[0])
    message = "{}日目の夜がやってきました。\n夜の行動に移ってください。".format(night_count)
    line_bot_api.push_message(group_id, TextSendMessage(text=message))
    #白確占い
    if night_count == 1 and first_f_telling == 1:
        with db:
            cur = db.execute("SELECT id FROM jinrou WHERE role='占い師'")
            rows = cur.fetchone()
        user_id = rows[0]
        with db:
            cur = db.execute("SELECT name FROM jinrou WHERE role NOT IN ('占い師', '人狼') AND status='alive'")
            rows = cur.fetchall()
            f_f_telling_name_list=[]
        for i in rows:
            f_f_telling_name_list.append(i[0])
        rand_n=random.randint(0, len(f_f_telling_name_list)-1)
        message = "初日白確占いの結果\n"\
                  "{}さんは人間です。".format(f_f_telling_name_list[rand_n])
        line_bot_api.push_message(user_id, TextSendMessage(text=message))
    night_count += 1
    global dead
    if dead == "無し":
        message = "夜が明けました。\n本日の犠牲者はいません。\n"\
                  "５分間で話し合いを行ってください。"
        line_bot_api.push_message(group_id, TextSendMessage(text=message))
    else :
        message = "夜が明けました。\n本日の犠牲者は「" + dead + "」です\n"\
                  "５分間で話し合いを行ってください。"
        line_bot_api.push_message(group_id, TextSendMessage(text=message))
        dead = "無し"
    #パン屋
    with db:
        cur=db.execute("SELECT status FROM jinrou WHERE role='パン屋'")
        rows = cur.fetchone()
    if len(rows[0]) != 0:
        if rows[0] == "alive":
            message = "パンが届きました。"
        else:
            message = "パンが届きませんでした。"
    else:
        message = "パンが届きませんでした。"
    line_bot_api.push_message(group_id, TextSendMessage(text=message))

    #本日の生存者のオフセットをリストに格納
    global list_alive
    list_alive = []
    for i in range(len(statusList)):
        if statusList[i] == "alive":
            list_alive.append(i)

    with db:
        cur=db.execute("update jinrou set status='alive' where status='gard'")
    #各個人に投票用カルーセル送信
    
    for i in range(len(statusList)):
        if statusList[i] == "alive":
            user_id = idList[i]
            alive_name = getouhyou(user_id)[0]
            alive_id = getouhyou(user_id)[2]
            message = TemplateSendMessage(alt_text="処刑選択",template=CarouselTemplate(columns=poll.execution(alive_name, user_id, alive_id, night_count)))
            line_bot_api.push_message(user_id, messages=message)

@app.route("/callback",methods=["POST"]) #どのURLが関数の引き金になるべきかをFlaskに伝える。
def callback():
    signature=request.headers["X-Line-Signature"] #署名の検証(LINEのサーバーからのリクエストにはX-Line-Signatureヘッダが付与されているので、それを検証している。)
    body=request.get_data(as_text=True)
    app.logger.info("Request body"+body)

    try:
        handler.handle(body,signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(FollowEvent)
def handle_follow(event):
    message = "このボットをグループに招待することで複数名で人狼ゲームを行うことができる。\n"\
              "またゲームに参加する場合はグループ内で発行されたゲームIDをここで入力する。"
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=message))

"""
@handler.add(UnfollowEvent)
def hanle_unfollow(event):
    your_id = event.source.user_id
    #友達削除時にユーザーIDの削除を行う
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS {}".format(your_id))
"""


#グループ参加時の処理
@handler.add(JoinEvent)
def handle_join(event):
    global step,roles,role_numbers,message_list,dead,group_id,game_id,url,night_count,first_f_telling
    night_count = 1
    first_f_telling = 0
    step = []
    roles = ["人狼", "狂人", "村人", "占い師", "霊媒師", "騎士", "パン屋"]
    url=["https://lh3.googleusercontent.com/ZCr8Bqdk6yo0PE49-B6erTLg1-aKD_zkDx1867XWYTBsAaSL3K-lBHNXDhK7zSuj84eyvhD0rcXNg1jJw8wyI1kNDbZoJBAkxEn3j9yD3MF-w8MdNcMECVn2OwMpPmpfabBrOUAMuPURFZd9dAp4gocVpTuYzbvns1iL0ubgsDbJK5hrS0aOWf5vQ1SmwQ_bN4Wt4p85pWxb4WCqWXO4WNl7zvShTbzUWygdKlSEXJ1QgYLgeQHP2IDS-aHf2ol00Z6h0pM3LA6MxC_HArfgt1VQYaBYzveVB9cYDEKrVvndAwiAHYvJ2ZltKmGfDhZi1i4H2KvUCD-bmW952BKyxllev2UBi1AyFT87-sOY-vNnoWbNHfr6qfo2rQdUbkfwoDGqMMyJVAPSJMKf4kJTaBae3OCowa6ufVMHyNRqgd0PJsu0V3wNG0rKiWw8rhLqt3wbC93S9xXUBieEt-Ybze9CXnjDp1FlDXVhxfc0BeNBqS_RXu34BzJw51gANllVtnGBblhyiEnmNx_O_jYaZcqdKxagVFWPLuMmiMeJolSa-wzMosQQLaW1rTMoZwh9QCjmMEZDcupG91EfW5NTcPfWSPxwk6RV1RiilHCUiRER4MO_gUZSrMQm1bR5g5nSNiHW5H6hLuSUA9m_stJw6OlHgM0cBRFd6mqWBiyI3GV9esdRylldq8dQ5OZ341fosXk7sr12tWHyrbqMX8VTVOY=w960-h540-no?authuser=0",
    "https://lh3.googleusercontent.com/GDlhh5JzhUV086FkolpVBQxMzIdFl8651BpyGcY5R0SXOiyJpYa1JzUIBHGmRRpJnvL8faDOiMG7JSdlp12zwkxlXHbd7eMBSf4nO3oF6oo_1mJuBHZK7ZXnbd9eGBSrQAxwBHw4BdY9DgN1RO_g3ZcqF8U0aMlnXb7bMUr1alf_9dvgkAhJvOWOCx9GlrTfbrxoVZho2fqA6CddEl-sNYS17krrl0vRZ-GyXRy9CIqs4sXgEd6N1cwAuArclxXJEYgQopJSAPADB-cqC5dlkxfaNvxSsQ4NBpTESyM9_llIiFOYtg7rke1L8h72_uvDfDseXtodm9EzPLkJKi3XIIoHfTR4QYME90MzoSf84XulhVFTRotmdwz1ytw4dcxfBqzia9mSA1HBAmBg0QqY1N8QLeJMgDVRJgD7MDlR1KE73p07c4aupF4dWtqNc9BOvnVTMt1yeoDcnez5CRMS4ywpCIyTVOAKUGGpOKe7B3E3y7RsgvZ5h-s-44ak4-LU5_r18xZmerBl3N9PHLsFqdvSykv_ni3aUPPyQU_Ysa0oy_aH9vWG8FEBCqB0Y4yo_AH3C3QX_n3QUFWBDM5yBwef25ECswyrVITeatEMqXYZd7yZOb-yAf-TIpv3zxKzp6NobpkvsUtn53MPV8wgDK9xMfCM5-fMiIY56JjkcUCf8TV7hABd1ckE24t9gdthUIU4dVrcwnxx5cOTimeiOnc=w960-h540-no?authuser=0",
    "https://lh3.googleusercontent.com/6j0wU2vuN2hlyOXhgMpeg15YJddukBlNc6etg2AMtWCSCX7rQtdEKO6cRo-A_VzNVil6y2Z8ZdEo_nBD-LCVejkWK3kjTJ5eibZ_0hJnBbmt_MlshrnExMWuvJu3tjccVfbex7BRrqMAC32o6aZqVAIIsOpk9tZYbTWrVk3a6EKlUewiYPS_4P3bj3rnOiJN2cZjzPB2m40XcX82YTGYv04ycb4VzuFEcbH2XevHPiw2zNMbD-6bcC70Qc2XkUIFirSpgYDy47jZ2yfIg36zQPUP0RXbHMaQ0qu1f1sZZnjJnkorWIRiLPOmY50MOg8Dp7tGW58rl4bv8H_C9cfn03PD_bVjfygaatJwyck7B8e27xeCdocEhjBR5HXhof-qWg1-T4N5BpqDRJxBNtDUoKbzmaUzs-taOR6R4i49dqgWQczYcvFRgImpDgiSoZPEJNgExEaRw69Wa_dG33r3aUrJZADicZYDYPYM8BDTbgciX0W-aCegIWthXy69Y2jxpfNrUMGSSTFs7cZxsHsJrnUx6U7__q6u8H4Aa4ke7NyCYvw62O2osFo9s-Tpu0Ver9e2sFyjGI1p8caGYa7GF8GCVreKID2HhP5NdyNJo-KvhS14BDFPOqtomnfjt3vIPg4rzqRqdID8PJoPh6JlAF0TDOpyol5mEZHUaa0hZNeVBo-MJggu4V3SlSlLm8RbySZZ1UZkqIeAL1I6K7RdXTI=w960-h540-no?authuser=0",
    "https://lh3.googleusercontent.com/SmvEOz9eJV6a1Lc2g7qcxkYSjCtGaSeu4BxAwKmVvgX2ZFKN-uDX-asSuuPhR98eEwUOf0OvvzXoa_NU1IM9pIYFPFF4qhCmPl78YYddUZwhyMjqiEX-vi3BsL__MlHzGFWIFQaf0kisci9s8B2RXC14DcpN8jApFs3yrAXCSgsVtoUi4YA0NCSwCVuQFDuYpEe-565DBPHH7a6dvva1v3hb5sGG9Jjla8GaFr7zVoAS4To6QxLkiSGOEKbpk7QVJtWb4cBQTBYoZH0eaY1nO5CtLB3xCadTOl2wGCPgqzxMbMKKOkZ_Obowxbtq7mBNA8kHeKVJjDkhnzZ0tUUaN-goIl2JIUav3ZxlgtpQ58SP_CTNT7DWTSmTWL3Ibq-ny9dOpK8fmDdLnkbL5EnjTCMWD4ycJ5kR8GqsapOvq4Df3FBMbFGFgFuT8piyaalD1MbT2FpaceROA6Zfd_z3GdyBCVbB6l4MGLO4rUp_sswpP4XsfGJCVUzWbHzTy1xL9IQAji8sU0ZJeXN1aBPaFbKkfeNE5NrvT5JTMODYw-iDu7C0jHZBI33P4L9np7Ai2HXL6Moxj4kIk1SS-eDBWU6nl6GX_53LDwsIIphMCrkKgkSerdwQ9mS5JMFRqD2mx6VogUqR5fIH0Yu4t6hMTDind3DAFd-PC1z16V7-5UAFkdzVAw7dJ3ejxl0IxBXAqPfiLm0sJwtcgC4r2izLamc=w960-h540-no?authuser=0",
    "https://lh3.googleusercontent.com/oCAq8PGUWsLEHZyJ4qECOP1PU-4NT6aO2EjbLdFShA5-IAt-0lGxwbfeuEVgIPWmi6pQWSuqBi51P4i-gzl7Ir5DKgX9cL-BkQoutUNOADERzjNBHqAi3y1RY4ZqS3Aojg5hQWfPjD9qG4bk_4m1t2a8IdTP2XhYumUttuFY04TARVoQ7nBjnpRCfLPKFI76HdnFBKmbdWNk4aiwnhPwoVlzGdpQyTtyn9QTP-J1_ntjekqgatYHl5GLNhvYreiDrQPGm9itlzeTqwrIOhGlownm1gSUC1lzmeO2j7_tPv7NmhYViDh6rx6-eWDN83ASC6u8K-nYvNlCNcBBNLwLSvf5vjG9uy6pc719pkeVgbbpEgubNw-QxmaBafMaBNYt-Okr2NgzwQgqJ8oVrujCFaHjMgpJXx5U-MW1pylyczAqxlcgP_i-mY57Df1DwV-k8FxG3KBD232mtCcX4UENxp9jMeB3EQ3di_RIJSwHtiUSLolmaBahUDkgBZ2w9ACkWOWtIYCsHcgBua5G4jf1JKYq3W4CZGiCYXYZsb55REsLbpYihph5bF_iuhvNAXCNEVmCHCsDrDAHU-WlIds7dQpco7Wp4foiUsKWDltwDXgZgGt54JM4BOdZORXsHAOuasPH9UvsfWA3ZqXlWA7PUAsTUDoACEKF37pnNwNLbSHS1rwhxuWViPzlf_L4xjOIha5IYdVrxoXsoqlqGgeUn0A=w1024-h576-no?authuser=0",
    "https://lh3.googleusercontent.com/I6ComkyhfqLbWzssRCsDIb-bpsugSIwdSaz9znlU6ioLCblaeL-5A4P3H7K6nDPZySxeQp_dYkfuB_gYIFIIwXwUbf6lSLsV6ahUIbZh-teQHh_46Inoqr08bTwt5wx7jkX3l_HY7Y-FBvdLGg2oMSc7p4QNkheLxNBjZ19t-rWQSdGmZKk5Li_SaZDN-9Wtq3uVEwBLYk9yo5hQLoJ0goKUKIQQwK4GmEmgvQogTPl9NIXtny_nbzGKSmMD1-CePELGK16R-j6dhFaUaCYz1H-Z4dXr5t9N4ok2m3c04ZB64XOdM7SzB5_QJ0jvGvbLqqxdF9gN7DZ6ik5H7G6ZXCPAgR-5cXcrLp2Qel8WHjdWo5yQDi0dSg1mYGVwwfcy3DabNYh_uu94LvHP4ReU9UOr4Z3czpBj0Tgke53hGcl0ROeDS8e476Zd9dr0qGJzvvVwrAm3QdWmyy2zWBsZWjRGRDxWyZ6m6Wiq0CgWAolFMRkC_E6aCoBsikbetcr6uAracZ1d26VMorlREVNqTKwivw13r3UxXnFbmZMTnIBU-gnKCbI0frrkM8fWVHgtwJPze2U6a1V4dIlDSaTMfoB2hZROXLcwUr0jlybMF19VEwcWqWVUeKb9Lq8s7wEUw7NGLpvKoA9LRASZY5c82X4M_Upb4RbBdwYud9uIvcBs6dy40TE8luuj6_GNJmt3G9YP8y4GRJPAY0jxJsch_LE=w1024-h576-no?authuser=0",
    "https://lh3.googleusercontent.com/fWxq6HvufM19T_WEEJESl0Nd-NF7ZCiSqI_W-xQ-O6uX587wtTPVYya6hqkT24oC5A07ceniOOf67_ME_r2VdNgeq_ZNwvhirJfJtg6Ja6p6dfT6_VjqG5Cke855pIxOjfxokFOeo6Txc7oEv8WVwVhNEEFng-C1yivO2ft26mYQdvJNvm7yMG5mK1DQHokUVOrllqeLuDrDNwHezcgq_Hk6cdTBG_qctAPn75AMnGt5yTphr5ntbzZ1L9sAo0rtR-AVU0ZE-WLsli-xYb0B_asFBcmVhTewKuT2X9Z1dI18sMLSvOeFMiRFXxVyR9nOMZ1YgpFBBmCjyd601qySAuOgSGk4V0ilGKNjUI2rRCuh-Tb1T-VOxFSlCHagrtGMYU_VaHp2E_XdSeStFCjQ-TQyzacBPnUbkg4rdk71OLz4f3RBuIDgo2LFF-fXdzhFub7Ec4ilip0c7JoL8FXZcF8ImpY_4vpERdt9OkePERtyOh0U0LmcYg06MIFfX6mqlKBhKcv08BPFGStce9EC4bXEwwy7nwewl8WmnoukbHYcdnFmlOauzrnJ3E7h6EqqwXLO5lvtcWdHiuEWabX9OPlDLBKELJc2ArWVlETfqcgBbwBlHwpZWEwh3uCFQhrraGA1WOYlPwLY8CoPFdthY57Umx7MfTWAnvHjgQsbVhrJWlo6nXfvxm_WF7i4McQU_TLKERpBqFYJ-0ny_qNhz0Y=w1024-h576-no?authuser=0"]
    role_numbers = []
    for i in range(len(roles)):
        role_numbers.append(0)
    message_list = []
    for i in range(len(roles)):
        message_list.append(0)
    dead = "無し" 
    group_id = event.source.group_id
    game_id = "".join(random.choices(string.ascii_letters + string.digits, k=8))
    message = "今回のゲームIDは\n{}\n"\
              "このゲームIDをボットとの個人チャットで送信するか参加ボタンを押すことで、"\
              "参加者として登録される。".format(game_id)
    line_bot_api.push_message(group_id, TextSendMessage(text=message))
    #ゲーム参加ボタン
    message = button.join_button()
    line_bot_api.push_message(group_id, messages=message)
    #役職選択ボタン
    message = TemplateSendMessage(
        alt_text="役職選択",
        template=CarouselTemplate(columns=button.carousel(roles, url))
    )
    line_bot_api.push_message(group_id, messages=message)
    #役職選択完了ボタン
    message = button.select_button()
    line_bot_api.push_message(group_id, messages=message)
    #初日白出し有無ボタン
    message = TemplateSendMessage(
        alt_text="初日白確有無",
        template=CarouselTemplate(columns=button.first_f_telling())
    )
    line_bot_api.push_message(group_id, messages=message)

#ゲーム用のテーブル作成
    query = "CREATE TABLE IF NOT EXISTS jinrou (" \
            "id char(33) PRIMARY KEY,"\
            "name varchar(10) NOT NULL,"\
            "role varchar(10) NOT NULL,"\
            "poll char(33) NOT NULL,"\
            "status varchar(10) NOT NULL)"
    with db:
        db.execute(query)  

@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    text = event.message.text
    #ゲームID受信時の処理
    if text == "再設定":
        if len(step) == 0:
            for i in range(len(roles)):
                role_numbers[i] = 0
            message = TemplateSendMessage(
                alt_text="カルーセル",
                template=CarouselTemplate(columns=button.carousel(roles, url)),
            )
            line_bot_api.reply_message(event.reply_token, messages=message)
            message = button.select_button()
            line_bot_api.push_message(group_id, messages=message)
        else:
            message = "すでに抽選を終えているので再設定はできません。"
            line_bot_api.reply_message(event.reply_token,TextSendMessage(text=message))
    elif text == "確認":
        for i in range(len(roles)):
            message_list[i] = "{} : {}人".format(roles[i],role_numbers[i])
        message = "\n".join(message_list)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
    elif text == "抽選":
        if len(step) == 0:
            line_bot_api.push_message(group_id, TextSendMessage(text="抽選中です...待ってて"))
            global nameList
            nameList = []
            #nameList = worksheet.get_name()
            with db:
                cur = db.execute("select name from jinrou")
                rows = cur.fetchall()
                for i in rows:
                    nameList.append(i[0])
            jinrou_list=[]
            role_list = []
            for i in range(len(roles)):
                for n in range(role_numbers[i]):
                    jinrou_list.append(roles[i])
            for i in range(len(nameList)):
                rand_n = random.randint(0, len(nameList)-1)
                while rand_n in role_list:
                    rand_n = random.randint(0, len(nameList)-1)
                role_list.append(rand_n)
                with db:
                    db.execute("UPDATE jinrou SET role='{}' WHERE name='{}'".format(jinrou_list[rand_n], nameList[i]))

            step.append(1)
            #抽選結果の通知
            global idList, roleList
            idList = []
            #nameList = worksheet.get_name()
            with db:
                cur = db.execute("select id from jinrou")
                rows = cur.fetchall()
                for i in rows:
                    idList.append(i[0])
            roleList = []
            #nameList = worksheet.get_name()
            with db:
                cur = db.execute("select role from jinrou")
                rows = cur.fetchall()
                for i in rows:
                    roleList.append(i[0])
            jinrou_Meibo_List = jinrou_Meibo()
            for i in range(len(idList)):
                message = "あなたの役職は\n「" + roleList[i] + "」\nです"
                line_bot_api.push_message(idList[i], TextSendMessage(text=message))
                time.sleep(1)
                if len(jinrou_Meibo_List)>=2:
                    if nameList[i] in jinrou_Meibo_List:
                        user_id=idList[i]
                        with db:
                            cur = db.execute("select name from jinrou where id not in ('{}') and role='人狼'". format(user_id))
                            rows = cur.fetchall()
                        otherjinrou=["他の人狼は、"]
                        for i in rows:
                            otherjinrou.append(i[0])
                        otherjinrou.append("です")
                        message = "\n".join(otherjinrou)
                        line_bot_api.push_message(user_id, TextSendMessage(text=message))
            message = "抽選完了です。個人チャットにて確認してください\n\n設定が完了したのでゲームを開始します。"
            line_bot_api.push_message(group_id, TextSendMessage(text=message))
            #ゲーム開始
            #初日占いありならここに追加
            #(１日目：夜...)
            game()
            #worksheet.overwrite(30, 1, "game関数終了")
        else:
            message = "抽選済みです。"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
    elif text == "タイマー":
        timer = 0
        timer_start = int(time.time())
        while timer != 10:
            timer_end = int(time.time())
            timer = timer_end - timer_start
        line_bot_api.push_message(group_id, TextSendMessage(text="finish"))
    elif text == "test":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="reply_message"))
        line_bot_api.push_message(group_id, TextSendMessage(text="push_message"))
    else:
        line_bot_api.reply_message(
            event.reply_token,TextSendMessage(text="しらない言葉だにぇ")) 
        #pass

@handler.add(PostbackEvent)
def handle_message(event):
    event_data = event.postback.data
    nameList = []
    with db:
        cur = db.execute("select name from jinrou")
        rows = cur.fetchall()
        for i in rows:
            nameList.append(i[0])
    idList = []
    with db:
        cur = db.execute("select id from jinrou")
        rows = cur.fetchall()
        for i in rows:
            idList.append(i[0])
    roleList = []
    with db:
        cur = db.execute("select role from jinrou")
        rows = cur.fetchall()
        for i in rows:
            roleList.append(i[0])
    if event_data == "select_button":
        count = 0
        for i in range(len(roles)):
            count = count + role_numbers[i]
        if len(nameList)==count :
            line_bot_api.push_message(group_id, TextSendMessage(text = "役職の人数を設定しました。"))
            line_bot_api.push_message(
                group_id, TextSendMessage(
                    text="再設定は「再設定」と入力する事で可能です。\n"\
                         "役職の人数確認は「確認」と入力してください。\n"\
                         "役職抽選に移る場合は「抽選」と入力してください。"\
                         "ただし抽選後は「再設定」不可となります。"
                )
            )
        else:
            line_bot_api.push_message(group_id, TextSendMessage(
                text="参加人数と役職の人数が一致していません。\n"\
                     "選択しなおしてください。"
            ))
            for i in range(len(roles)):
                role_numbers[i] = 0
            #役職選択ボタン
            message = TemplateSendMessage(
                alt_text="役職選択",
                template=CarouselTemplate(columns=button.carousel(roles, url))
            )
            line_bot_api.push_message(group_id, messages=message)
            #役職選択完了ボタン
            message = button.select_button()
            line_bot_api.push_message(group_id, messages=message)
    elif event_data == "join_button":
        user_id = event.source.user_id
        profile = line_bot_api.get_profile(user_id)
        with db:
            db.execute("INSERT INTO jinrou VALUES ('{}', '{}', '', '', 'alive')".format(user_id, profile.display_name))
        message = "ゲームID「" + game_id + "」のプレイヤーに登録しました。"
        line_bot_api.push_message(user_id, TextSendMessage(text=message))
    elif event_data[:11] == "f_f_telling":
        if event_data[11] == 1:
            first_f_telling = 1
        else:
            first_f_telling = 0
    #占いの結果送信
    elif event_data[:7] == "fortune":
        count_i = 8
        name = []
        for i in event_data[count_i:]:
            if i == "/":
                count_i += 1
                break
            else:
                count_i += 1
                name.append(i)
        name = "".join(name)
        role = []
        for i in event_data[count_i:]:
            role.append(i)
        role = "".join(role)

        for i in range(len(roleList)):
            if roleList[i]=='占い師':
                user_id=idList[i]
        message = "＜　占い結果　＞\n" + name + ":" + role
        line_bot_api.push_message(user_id, TextSendMessage(text=message))
    #霊能者の結果を返す
    elif event_data[:6] == "reibai":
        count_i = 7
        name = []
        for i in event_data[count_i:]:
            if i == "/":
                count_i += 1
                break
            else:
                count_i += 1
                name.append(i)
        name = "".join(name)
        role = []
        for i in event_data[count_i:]:
            role.append(i)
        role = "".join(role)
        for i in range(len(roleList)):
            if roleList[i]=='霊媒師':
                user_id=idList[i]
        message = "＜　霊媒結果　＞\n" + name + ":" + role
        line_bot_api.push_message(user_id, TextSendMessage(text=message))
    #人狼の投票結果反映
    elif event_data[:7] =="jinkill":
        name = []
        for i in event_data[8:]:
            name.append(i)
        name = "".join(name)
        with db:
            db.execute("UPDATE jinrou status='death' where name='{}'".format(name))

                #message = "＜　人狼結果　＞\n"  + "本日の犠牲者は" + jintouhyou[int(event_data[7])] + "です"
                #line_bot_api.push_message(group_id, TextSendMessage(text=message))
        dead = name
    #処刑投票の結果をシートに記入する
    elif event_data[:9] == "execution":
        with db:
            db.execute("UPDATE jinrou SET poll='{}' WHERE id='{}'".format(event_data[42:75], event_data[9:42]))
        check_poll = []
        pollList = []
        with db:
            cur = db.execute("select poll from jinrou")
            rows = cur.fetchall()
        for i in rows:
            pollList.append(i[0])
        for i in list_alive:
            check_poll.append(pollList[i])
        if '                                 ' not in check_poll:
            #投票リストの要素数カウント変数
            execution_number = 0
            #処刑者のリスト
            executed = []
            #投票最頻要素をexecutedに格納
            for i in set(check_poll):
                if execution_number < check_poll.count(i):
                    execution_number = check_poll.count(i)
                    #最頻が更新されたので処刑リストも更新
                    executed = [i]
                elif execution_number == check_poll.count(i):
                    #投票最頻重複の際にリストにappend
                    executed.append(i)
                else:
                    pass
            if len(executed) != 1:
            #最頻重複の際にランダムで処刑決定、executed[0]に追加
                executed = [ executed[random.randint(0, len(executed)-1)] ]
            else:
                pass
            for i in range(len(idList)):
                if idList[i] == executed[0]:
                    break
            message = "全員の投票が完了しました。\n"\
                    "投票の結果、「" + nameList[i] + "」さんが処刑されます。"
            line_bot_api.push_message(group_id, TextSendMessage(text=message))
            #処刑されたプレイヤーの状態をdeathに変更
            with db:
                db.execute("UPDATE jinrou SET status='death' WHERE id='{}'".format(executed[0]))

            #人狼陣営と村人陣営の人数比較
            #jinrou_Meibo_List=jinrou_Meibo()
            #ningen_Meibo_List=ningen_Meibo()
            with db:
                cur=db.execute("select count(*) from jinrou where role='人狼' and status='alive'")
                jinrou_num=cur.fetchone()[0]
                cur=db.execute("select count(*) from jinrou where role!='人狼' and status='alive'")
                ningen_num=cur.fetchone()[0]
            #意図的にningen_numにしています。
            if ningen_num==0:
                message = "＜　結果発表　＞\n" "市民側の勝利です"
                line_bot_api.push_message(group_id, TextSendMessage(text=message))
            elif jinrou_num==ningen_num:
                message = "＜　結果発表　＞\n" "人狼側の勝利です"
                line_bot_api.push_message(group_id, TextSendMessage(text=message))
            else:
            #勝敗が決定しなかった場合なので、夜の行動に移る
                message = "{}日目の夜がやってきました。\n各自夜の行動に移ってください。".format(night_count)
                line_bot_api.push_message(group_id, TextSendMessage(text=message))
                with db:
                    cur=db.execute("select id from jinrou where status='alive' and role='占い師'")
                    rows=cur.fetchone()
                try:
                    user_id=rows[0]
                except:
                    pass
                touhyou_name, touhyou_role, touhyou_id =getouhyou(user_id)
                message = TemplateSendMessage(alt_text="占い選択",template=CarouselTemplate(columns=poll.fortune_telling(touhyou_name, touhyou_role)))
                line_bot_api.push_message(user_id, messages=message)
                #霊媒師の投票
                with db:
                    cur=db.execute("select id from jinrou where status='alive' and role='霊媒師'")
                    rows=cur.fetchone()
                try:
                    user_id=rows[0]
                    death_note_List_n, death_note_List_r=death_note()
                    message = TemplateSendMessage(alt_text="霊媒師選択",template=CarouselTemplate(columns=poll.reibai_telling(death_note_List_n, death_note_List_r)))
                    line_bot_api.push_message(user_id, messages=message)
                except:
                    pass
                #人狼のキル投票
                with db:
                    cur=db.execute("select id from jinrou where status='alive' and role='人狼'")
                    rows=cur.fetchone()
                try:
                    user_id=rows[0]
                    jintouhyou=jinrou_touhyou()
                    message = TemplateSendMessage(alt_text="人狼のキル",template=CarouselTemplate(columns=poll.jinrou_killing(jintouhyou)))
                    line_bot_api.push_message(user_id, messages=message)
                except:
                    pass
                #騎士の投票
                with db:
                    cur=db.execute("select id from jinrou where status='alive' and role='騎士'")
                    rows=cur.fetchone()
                try:
                    user_id=rows[0]
                    touhyou_name=getouhyou(user_id)[0]
                    message = TemplateSendMessage(alt_text="騎士選択",template=CarouselTemplate(columns=poll.garding(touhyou_name)))
                    line_bot_api.push_message(user_id, messages=message)
                except:
                    pass
                game()

    #騎士の投票結果反映
    elif event_data[:5] =="kishi":
        name = []
        for i in event_data[6:]:
            name.append(i)
        name = "".join(name)
        with db:
            cur=db.execute("update jinrou set status='gard' value where status='alive' and name=('{}')". format(name))
        with db:
            cur=db.execute("select id from jinrou where status='alive' and role='騎士'")
            rows=cur.fetchone()
            user_id=rows[0]
        message = "＜　騎士結果　＞\n"  + "本日は" + name + "を守ります"
        line_bot_api.push_message(user_id, TextSendMessage(text=message))
    #役職の人数選択のカルーセル
    else:
        role_id = int(event_data[20])
        role_number = int(event_data[21])
        role_numbers[role_id] = role_number

@handler.add(LeaveEvent)
def handle_message(event):
    with db:
        db.execute("DROP TABLE jinrou")



#アプリの実行
if __name__=="__main__":
    port=int(os.getenv("PORT",5000))
    app.run(host="0.0.0.0",port=port)
