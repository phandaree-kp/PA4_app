import streamlit as st
import openai
import pandas as pd
import json

#sidebar สำหรับใส่ API Key
user_api_key = st.sidebar.text_input("🔑 กรุณากรอก OpenAI API Key(ㅅ´ ˘ `)", type="password")

prompt_template = """
สมมติว่าคุณเป็นนักพยากรณ์ดวงที่เน้นคำทำนายแบบปั่น ขำขันสุด ๆ ฮาน้ำตาเล็ด 
คุณจะได้รับชื่อเพื่อน วันเกิด (วันในสัปดาห์) และนิสัยของเพื่อน
สร้างคำทำนายสุดฮาใน 5 หมวดดังนี้:
1. การงาน
2. การเงิน
3. สุขภาพ
4. ความรัก
5. โชคลาภ
จากนั้นส่งคำทำนายในรูปแบบ JSON array ที่มีโครงสร้างดังต่อไปนี้ ตัวอย่างเช่น:
[
    {"category": "การงาน", "prediction": "เจ้านายชมเชย! ( • ̀ω•́ )✧ แต่ไม่ได้ขึ้นเงินเดือน ╥‸╥"},
    {"category": "การเงิน", "prediction": "ได้เงินมาไวヾ(｡✪ω✪｡)ｼ💰 แต่หมดไปไวกว่า ∘ ∘ ∘ 💸( °ヮ° ) ?"},
    {"category": "สุขภาพ", "prediction": "ปวดหลังเพราะนั่งเล่นเกมส์ยันเช้า ( TᗜT)🎮"},
    {"category": "ความรัก", "prediction": "คนโสดจะเจอคนถูกใจ (｡>\\<) แต่เขาดันมีแฟนแล้ว..."},
    {"category": "โชคลาภ", "prediction": "โชคลาภกำลังรอคุณอยู่ในมุมที่ไม่คาดคิด—อาจจะเป็นเงินในเครื่องซักผ้าที่ลืมหยิบออกจากกระเป๋ากางเกง!🧺🧼"}
]
ไม่ต้องอธิบายเพิ่มเติม ส่งแค่ JSON array เท่านั้น
""" 

#ส่วนหัวของแอป
st.title("🌟🔮🔥 ระบบพยากรณ์ดวงเพื่อนแบบปั่น 🔥🔮🌟")
st.write("กรอกข้อมูลเพื่อนของคุณ👧🏻🧒🏻💞 (สูงสุด 5 คน) เพื่อดูคำทำนายสุดฮา!")

#กรอกข้อมูลเพื่อนทีละคน (สูงสุด 5 คน)
friends_data = []
for i in range(1, 6):
    st.subheader(f"เพื่อนคนที่ {i} 🏃🏻‍♂️💨")
    friend_name = st.text_input(f"ชื่อเพื่อนคนที่ {i}", key=f"name_{i}")
    birthday = st.selectbox(f"วันเกิดคนที่ {i}", 
                            ["วันอาทิตย์", "วันจันทร์", "วันอังคาร", 
                             "วันพุธกลางวัน", "วันพุธกลางคืน", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์"], 
                            key=f"birthday_{i}")
    behavior = st.text_input(f"นิสัยหรือพฤติกรรมเด่นของเพื่อนคนที่ {i}", 
                             placeholder="เช่น ชอบเบี้ยวนัด ติดแฟน ตอนเมาเคยอุ้มหมากลับบ้าน", key=f"behavior_{i}")
    
    if friend_name and birthday and behavior:
        friends_data.append({
            "name": friend_name,
            "birthday": birthday,
            "behavior": behavior
        })

#ปุ่มกดเพื่อขอคำทำนาย
if st.button("(๑'ᵕ'๑)⸝*🔮 ดูดวงง!"):
    if not user_api_key:
        st.error("กรุณาใส่ API Key ก่อนนะงั้ฟ! (ㅅ •᷄ ₃•᷅ )")
    elif not friends_data:
        st.error("กรุณากรอกข้อมูลเพื่อนอย่างน้อย 1 คนน้า (๑>؂•̀๑)")
    else:
        st.info("⏳ กำลังสร้างเรื่อง เอ้ย! สร้างคำทำนาย... โปรดรอสักครู่ ตรู้ดๆ")
        openai.api_key = user_api_key
        
        results = []
        for friend in friends_data:
            name, birthday, behavior = friend["name"], friend["birthday"], friend["behavior"]
            messages = [
                {"role": "system", "content": prompt_template},
                {"role": "user", "content": f"ชื่อ: {name}, วันเกิด: {birthday}, นิสัย: {behavior}"}
            ]
            
            try:
                response = openai.ChatCompletion.create(
                    model = "gpt-4o-mini", #รอดูอีกทีว่าจาซื้อ model ตุวไหน เหมือนคำสั่งตรง response จะไม่เหมือนกันด้วย
                    messages = messages
                )
                horoscope_json = response.choices[0].message['content']
                horoscope_list = json.loads(horoscope_json)
                
                for prediction in horoscope_list:
                    results.append({
                        "Name": name,
                        "Birthday": birthday,
                        "Behavior": behavior,
                        "Category": prediction["category"],
                        "Prediction": prediction["prediction"]
                    })
            except Exception as e:
                results.append({
                    "Name": name,
                    "Birthday": birthday,
                    "Behavior": behavior,
                    "Category": "Error",
                    "Prediction": str(e)
                })

        #สร้าง DataFrame
        df = pd.DataFrame(results)
        
        #แสดงผล
        st.subheader("📋 คำทำนายในรูปแบบตาราง")
        st.dataframe(df)

        #ดาวน์โหลด CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label = "📥 ดาวน์โหลดคำทำนาย (CSV)",
            data = csv,
            file_name ="friends_horoscope.csv",
            mime ='text/csv'
        )
