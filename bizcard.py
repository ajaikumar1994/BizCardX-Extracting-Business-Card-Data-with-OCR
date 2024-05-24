import easyocr
import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
import pandas as pd
from PIL import Image
import re
import io
import sqlite3


def image_details(image_input):
  image_inputs=Image.open(image_input)
  image_array=np.array(image_inputs)
  reader=easyocr.Reader(["en"])
  text=reader.readtext(image_array,detail=0)
  return image_inputs,text

def extracted_text(extracted_data):
  data={"NAME":[],"DESIGNATION":[],"COMPANY_NAME":[],"CONTACT":[],"WEB_PAGE":[],"MAIL_ID":[],"ADDRESS":[],"PINCODE":[]}

  data["NAME"].append(extracted_data[0])
  data["DESIGNATION"].append(extracted_data[1])

  for i in range(2,len(extracted_data)):
    if extracted_data[i].startswith("+") or (extracted_data[i].replace("-","").isdigit() and "-" in extracted_data[i]):
      data["CONTACT"].append(extracted_data[i])

    elif "@" in extracted_data[i] and ".com" in extracted_data[i]:
        data["MAIL_ID"].append(extracted_data[i])

    elif "WWW" in extracted_data[i] or "www" in extracted_data[i] or "Www" in extracted_data[i] or "wWW" in extracted_data[i] or "WWw" in extracted_data[i] or "wwW" in extracted_data[i] or "wWw" in extracted_data[i]:
        small=extracted_data[i].lower()
        data["WEB_PAGE"].append(small)

    elif "TamilNadu" in extracted_data[i] or "Tamil Nadu" in extracted_data[i] or extracted_data[i].isdigit():
        data["PINCODE"].append(extracted_data[i])

    elif re.match(r'^[A-Za-z]',extracted_data[i]):
        data["COMPANY_NAME"].append(extracted_data[i])

    else:
      remove_colon=re.sub(';,',' ',extracted_data[i])
      data["ADDRESS"].append(remove_colon)

  for key,value in data.items():
    if len(value)>0:
      concadinate=" ".join(value)
      data[key]=[concadinate]
    else:
      value="na"
      data[key]=[value]

  return data

#streamlit part


st.set_page_config(layout="wide")
st.title("Extracting Business Card Data with OCR")


with st.sidebar:
  select= option_menu("MAIN MENU",["HOME","EXTRACT AND SAVE","DELETE"])

if select == "HOME":
  st.image(r"/content/optical-character-recognition.jpg",width=950)
  st.markdown("### :blue[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")
  st.write("### :green[**About :**] Bizcard is a Python application designed to extract information from business cards.")
  st.write('### The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.')
  st.video(r"/content/What is Optical Character Recognition (OCR)_ and how does it work_.mp4")
elif select == "EXTRACT AND SAVE":
  st.image(r"/content/ocr.jpg",width=950)
  col1,col2=st.columns(2)
  with col1:
    img=st.file_uploader("UPLOAD A IMAGE",type=["png","jpg","jpng"])

  if img is not None:
    with col2 :

      st.image(img,width=425)

    image_input,text=image_details(img)
    text_data=extracted_text(text)

    if text:
      st.success("text extreacted successfully")

    df=pd.DataFrame(text_data)
    image_bites=io.BytesIO()
    image_input.save(image_bites,format="PNG")

    image_data=image_bites.getvalue()
    image_bites_data={"IMAGE":[image_data]}


    df=pd.DataFrame(text_data)

    df1=pd.DataFrame(image_bites_data)

    final_data=pd.concat([df,df1],axis=1)
    st.dataframe(final_data)

  save_button=st.button("save",use_container_width=True)

  if save_button:
      mydb=sqlite3.connect("bizcard.db")
      cursor=mydb.cursor()

      #table creation

      create_query='''CREATE TABLE IF NOT EXISTS BIZCARD_DETAILS (NAME varchar(225),
                                                                  DESIGNATION varchar(225),
                                                                  COMPANY_NAME varchar(225),
                                                                  CONTACT varchar(225),
                                                                  WEB_PAGE varchar(225),
                                                                  MAIL_ID varchar(225),
                                                                  ADDRESS varchar(255),
                                                                  PINCODE varchar(255),
                                                                  IMAGE text
                                                                  )'''


      cursor.execute(create_query)
      mydb.commit()

      insert_querry='''INSERT INTO BIZCARD_DETAILS  (NAME,DESIGNATION,COMPANY_NAME,CONTACT,WEB_PAGE,MAIL_ID,ADDRESS,PINCODE,IMAGE)
                                                      values(?,?,?,?,?,?,?,?,?)'''
      datas= final_data.values.tolist()
      cursor.executemany(insert_querry,datas)
      mydb.commit()

      st.success(" saved successfully")


  options=st.radio("select the options",["***PREVIEW/MODIFY***","PREVIEW","MODIFY"])
  if options=="***PREVIEW/MODIFY***":
    col1,col2=st.columns(2)
    with col1:
      st.image(r"/content/1000_F_303981738_1s8t2JvUDyfBKsHUmR01LZhEJBsJTgML.jpg",width=200)
    with col2:  
      st.image(r"/content/mofify.jpg",width=200)

  if options=="PREVIEW":
    mydb=sqlite3.connect("bizcard.db")
    cursor=mydb.cursor()
    querry='''SELECT * FROM BIZCARD_DETAILS '''
    cursor.execute(querry)
    table=cursor.fetchall()
    mydb.commit()
    df2=pd.DataFrame(table,columns=("NAME","DESIGNATION","COMPANY_NAME","CONTACT","WEB_PAGE","MAIL_ID","ADDRESS","PINCODE","IMAGE"))
    st.dataframe(df2)

  if options=="MODIFY":
    mydb=sqlite3.connect("bizcard.db")
    cursor=mydb.cursor()
    querry='''SELECT * FROM BIZCARD_DETAILS '''
    cursor.execute(querry)
    table=cursor.fetchall()
    mydb.commit()
    df2=pd.DataFrame(table,columns=("NAME","DESIGNATION","COMPANY_NAME","CONTACT","WEB_PAGE","MAIL_ID","ADDRESS","PINCODE","IMAGE"))
    col1,col2=st.columns(2)
    with col1:
      selected_name=st.selectbox("NAME",df2["NAME"])
      st.write(f"EXTRACTED INFORMATION OF {selected_name}")
    df3=df2[df2["NAME"]== selected_name]
    st.dataframe(df3)
    df4=df3.copy()
    col1,col2=st.columns(2)
    with col1:
      mo_name=st.text_input("NAME",df3["NAME"].unique()[0])
      mo_designation=st.text_input("DESIGNATION",df3["DESIGNATION"].unique()[0])
      mo_company_name=st.text_input("COMPANY_NAME",df3["COMPANY_NAME"].unique()[0])
      mo_contact=st.text_input("CONTACT",df3["CONTACT"].unique()[0])
      mo_web_page=st.text_input("WEB_PAGE",df3["WEB_PAGE"].unique()[0])

      df4["NAME"]=mo_name
      df4["DESIGNATION"]=mo_designation
      df4["COMPANY_NAME"]=mo_company_name
      df4["CONTACT"]=mo_contact
      df4["WEB_PAGE"]=mo_web_page
    with col2:
      mo_mail_id=st.text_input("MAIL_ID",df3["MAIL_ID"].unique()[0])
      mo_addres=st.text_input("ADDRESS",df3["ADDRESS"].unique()[0])
      mo_pincode=st.text_input("PINCODE",df3["PINCODE"].unique()[0])
      mo_image=st.text_input("IMAGE",df3["IMAGE"].unique()[0])

      df4["MAIL_ID"]=mo_mail_id
      df4["ADDRESS"]=mo_addres
      df4["PINCODE"]=mo_pincode
      df4["IMAGE"]=mo_image
    st.write(f"UPDATED INFORMATION OF {selected_name}")
    st.dataframe(df4)

    cl1,col2=st.columns(2)
    with col1:
      modify=st.button("UPDATE",use_container_width=True)
    if modify:

      mydb=sqlite3.connect("bizcard.db")
      cursor=mydb.cursor()

      cursor.execute(f"DELETE FROM BIZCARD_DETAILS WHERE NAME='{selected_name}'")
      mydb.commit()

      insert_querry='''INSERT INTO BIZCARD_DETAILS  ("NAME","DESIGNATION","COMPANY_NAME","CONTACT","WEB_PAGE","MAIL_ID","ADDRESS","PINCODE","IMAGE")
                                                      values(?,?,?,?,?,?,?,?,?)'''
      datas= df4.values.tolist()
      cursor.executemany(insert_querry,datas)
      mydb.commit()

      st.success("updated  successfully")

elif select == "DELETE":
    mydb=sqlite3.connect("bizcard.db")
    cursor=mydb.cursor()
    querry='''SELECT * FROM BIZCARD_DETAILS '''
    cursor.execute(querry)
    table=cursor.fetchall()
    mydb.commit()
    df5=pd.DataFrame(table,columns=("NAME","DESIGNATION","COMPANY_NAME","CONTACT","WEB_PAGE","MAIL_ID","ADDRESS","PINCODE","IMAGE"))
    selected_name=st.selectbox("NAME",df5["NAME"])
    df6=df5[df5["NAME"]==selected_name]
    st.dataframe(df6)
    delete=st.button("DELETE",use_container_width=True)
    if delete:
      st.image(r"/content/caution.jpg",width=850)
      cursor.execute(f"DELETE FROM BIZCARD_DETAILS WHERE NAME='{selected_name}'")
      mydb.commit()
      st.success("DELETED SUCCESSFULLY")


