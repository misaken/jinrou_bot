import time, os, psycopg2
from linebot.models import CarouselColumn, PostbackAction, TemplateSendMessage, ButtonsTemplate

DATABASE_URL = os.environ['DATABASE_URL']

class button:
    #カルーセルの表示
    def carousel(roles, n):
        columns = [
            CarouselColumn(
                thumbnail_image_url=n[i],
                title = roles[i],
                text = "選択肢を選んでください。",
                actions = [
                    PostbackAction(
                        label = "1人",
                        data = "action=click&itemid={}1".format(i),
                    ),
                    PostbackAction(
                        label = "２人",
                        data = "action=click&itemid={}2".format(i),
                    ),
                    PostbackAction(
                        label = "３人",
                        data = "action=click&itemid={}3".format(i),
                    ),
                ]
            )
            for i in range(len(roles))
        ]
        return columns

    #完了ボタン
    def select_button():
        message = TemplateSendMessage(
            alt_text="完了ボタン",
            template=ButtonsTemplate(
                text="役職選択完了したらおして",
                title="完了ボタン",
                actions=[
                    PostbackAction(
                        label="設定完了",
                        data="select_button"
                    )
                ]
            )
        )
        return message
    #参加ボタン
    def join_button():
        message = TemplateSendMessage(
            alt_text="参加ボタン",
            template=ButtonsTemplate(
                text="参加する人はおして",
                title="参加ボタン",
                actions=[
                    PostbackAction(
                        label="参加",
                        data="join_button"
                    )
                ]
            )
        )
        return message
    #初日白確占いの有無設定
    def first_f_telling():
        columns = [
            CarouselColumn(
                thumbnail_image_url="https://lh3.googleusercontent.com/RppYkPr19aFRHRZwo3321ZKrQgh5dHmX1Rk4XaHWYRT1sZtC22u7HiHTIBXkNrbN5YYekJmSrer8jEMbgb2Wif8R0_CyUnhyUjoNF0eah76oY77fP5viHH8ZF9FQ6XawZU_iEpmYh9Jf9Y_jmc-ZsS5SC-EjWL7EzbmNyW9HSJclocGnTRvhtLBm7NqgDHJFEsWruZJx3_fpfS0RjEwtG4lXPEzdBNnq4FbOiT14h6ByqBYVgGmnVLGemyo1Tz_6xizmr9W8aL7APzFR7nqv3CpGPVuCtbBp9jsBw4CID8N-DmWqx5vZuIRBzht5CpCzw8dki6uioMFRlHt99MW-uZCJwvLgJV6QiPDVF1UYEO6IS8PHUhf10e0eHMx4ylQGm7OxEyGaig1uuHbWLNdrnBmXZm00YFVCPzziRhFRJZQCcI2qvcBEUOrG95NbnnzZb3NMtJ75q9GPCuBxX9XlZydhwGyARsaY7ZlR40ITeZ13Q8kArhzmrZ975pITp2DeMB_ckpD-1z8KRWJgYQNCYf1qMVwokIxZy9FVOZn8H7ubkKlDt8IhmGp0hDNFk1zxDGmC12xZujbJPe-ljrV-LSIJytUQ3ujDhdFtbYhS_FxTE-G7MxikFYqoO7luF3Qy8OOIlcnkJl-WdHh_fWUohJZsFw1yVdOKkl4Bc-HuCntpDbjxDbm6oqy1eDdNU20QqzLne-axJdaDLvaa63ajsYo=w960-h546-no?authuser=0",
                title = "初日白確出有無設定",
                text = "選択肢を選んでください。",
                actions = [
                    PostbackAction(
                        label = "有",
                        data = "f_f_telling1",
                    ),
                    PostbackAction(
                        label = "無",
                        data = "f_f_telling0",
                    ),
                ]
            )
        ]
        return columns

class poll:
    def fortune_telling(touhyou_name, touhyou_role):
        columns = [
            CarouselColumn(
                thumbnail_image_url="https://lh3.googleusercontent.com/SmvEOz9eJV6a1Lc2g7qcxkYSjCtGaSeu4BxAwKmVvgX2ZFKN-uDX-asSuuPhR98eEwUOf0OvvzXoa_NU1IM9pIYFPFF4qhCmPl78YYddUZwhyMjqiEX-vi3BsL__MlHzGFWIFQaf0kisci9s8B2RXC14DcpN8jApFs3yrAXCSgsVtoUi4YA0NCSwCVuQFDuYpEe-565DBPHH7a6dvva1v3hb5sGG9Jjla8GaFr7zVoAS4To6QxLkiSGOEKbpk7QVJtWb4cBQTBYoZH0eaY1nO5CtLB3xCadTOl2wGCPgqzxMbMKKOkZ_Obowxbtq7mBNA8kHeKVJjDkhnzZ0tUUaN-goIl2JIUav3ZxlgtpQ58SP_CTNT7DWTSmTWL3Ibq-ny9dOpK8fmDdLnkbL5EnjTCMWD4ycJ5kR8GqsapOvq4Df3FBMbFGFgFuT8piyaalD1MbT2FpaceROA6Zfd_z3GdyBCVbB6l4MGLO4rUp_sswpP4XsfGJCVUzWbHzTy1xL9IQAji8sU0ZJeXN1aBPaFbKkfeNE5NrvT5JTMODYw-iDu7C0jHZBI33P4L9np7Ai2HXL6Moxj4kIk1SS-eDBWU6nl6GX_53LDwsIIphMCrkKgkSerdwQ9mS5JMFRqD2mx6VogUqR5fIH0Yu4t6hMTDind3DAFd-PC1z16V7-5UAFkdzVAw7dJ3ejxl0IxBXAqPfiLm0sJwtcgC4r2izLamc=w960-h540-no?authuser=0",
                title = "占いの実行",
                text = "占いたい人を次から選んでください",
                actions = [
                    PostbackAction(
                        label=touhyou_name[i],
                        data = "fortune/{}/{}".format(touhyou_name[i], touhyou_role[i]),
                    ),
                ]
            )
            for i in range(len(touhyou_name))
        ]
        return columns

    def jinrou_killing(jintouhyou):
        columns = [
            CarouselColumn(
                thumbnail_image_url="https://lh3.googleusercontent.com/iXPSFu3lh7ueZyzszr93Kel8F1QBdpnAoJmWnGRmBq0DV6EibHx81J8-V4As_nWuvqiOr4v22FIJJya2D4jrcWmyHoWFzhIYeiYsesqn5LZL0-pNNGfTufxioVJNkVhJjL4HhmNN26a6XUc_W902Vhq4GjVa2C2qVJ75U-DBtEykO9Rk4zVO2_ARdjDoJJB_-P-bRvJM80ELA2kv1Biwvv-YRPTwLECykZP1en_E-5wre_fgCJOutCBcg3jBkRRFJijk63xC8QylomhxPa2-mUYz7fMq7qlHzjSpzbUWERpiSdcvix8vjWDdA31eIboBFqfvjp2_QSp7JNlQHB5UBrciv40sTfjoXFrwry8-nRODUAFJPqYBDyBw-gfBCKiHYF_tLWjjoLzmROYO9LU0uun6kjp1NC0FcwMhK_l6ZCZDrF5RpVkpSwXJPRXfnnj3mwcolRHohT2TAEM-DsuSfqrN4PQudPJmCTLBqZhfhqaDOoRX9lKgLrLlHXOn0jcrXQcdVel9MVEQbZqRVH68OfafK4JAbWZV-QA9odCUUUWbcRENZso7Wg-iTH72l8Ng2bO_0VroxV2cOSX9mkJcjbpaQiYi_P-PKjumdV_8gwt3bX5K-_0LwwYvYiodTBOaWMM-2jSRwZGBN4owZwzU7Ya0igYVfyx6UJZ_8hXp-ZvDodUyrP5EHBPhn9AcHpI3RyPJ3eyJlx_nkJUcF-Bjb04=w960-h554-no?authuser=0",
                title = "人狼キル",
                text = "殺したい人を次から選んでください",
                actions = [
                    PostbackAction(
                        label=jintouhyou[i],
                        data = "jinkill/{}".format(jintouhyou[i]),
                    ),
                ]
            )
            for i in range(len(jintouhyou))
        ]
        return columns

    def reibai_telling(death_note_List_n, death_note_List_r):
        columns = [
            CarouselColumn(
                thumbnail_image_url="https://lh3.googleusercontent.com/4HtgBz4gL-1BVLG54iFNBgQTzNRatLDAaCzlUsWnZEpds96ZGK0npgBpTnpgGczJDq1esxkX1ggHOuNWqFiZC2xnCYLi290X-ILy9mxs2L5UjtKEnNewRc3aaGe_fT7WcA=w1280",
                title = "霊媒師の実行",
                text = "占いたい人を次から選んでください",
                actions = [
                    PostbackAction(
                        label=death_note_List_n[i],
                        data = "reibai/{}/{}".format(death_note_List_n[i], death_note_List_r[i]),
                    ),
                ]
            )
            for i in range(len(death_note_List_n))
        ]
        return columns

    def garding(touhyou):
        columns = [
            CarouselColumn(
                thumbnail_image_url="https://lh3.googleusercontent.com/4HtgBz4gL-1BVLG54iFNBgQTzNRatLDAaCzlUsWnZEpds96ZGK0npgBpTnpgGczJDq1esxkX1ggHOuNWqFiZC2xnCYLi290X-ILy9mxs2L5UjtKEnNewRc3aaGe_fT7WcA=w1280",
                title = "ガードの実行",
                text = "ガードしたい人を次から選んでください",
                actions = [
                    PostbackAction(
                        label=touhyou[i],
                        data = "kishi/{}".format(touhyou[i]),
                    ),
                ]
            )
            for i in range(len(touhyou))
        ]
        return columns
    def execution(alive_name, user_id, alive_id, night_count):
        columns = [
            CarouselColumn(
                thumbnail_image_url="https://lh3.googleusercontent.com/4HtgBz4gL-1BVLG54iFNBgQTzNRatLDAaCzlUsWnZEpds96ZGK0npgBpTnpgGczJDq1esxkX1ggHOuNWqFiZC2xnCYLi290X-ILy9mxs2L5UjtKEnNewRc3aaGe_fT7WcA=w1280",
                title = "{}日目の処刑投票".format(night_count),
                text = "本日処刑する人に投票してください",
                actions = [
                    PostbackAction(
                        label=alive_name[i],
                        data = "execution{}{}".format(user_id, alive_id[i]),
                    ),
                ]
            )
            for i in range(len(alive_name))
        ]
        return columns
    
class DB:
    def __init__(self):
        self.con = None
        self.cur = None
    def __enter__(self):
        self.con =psycopg2.connect(DATABASE_URL)
        self.cur = self.con.cursor()
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.con = None
            self.cur = None
            return False
        self.con.commit()
        self.cur.close()
        self.con.close()
        self.con = None
        self.cur = None
        return True
    def execute(self, query):
        self.cur.execute(query)
        return self.cur
