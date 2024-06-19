import easyocr
import pandas as pd
import streamlit as st
import numpy as np
import sqlite3
import re
import io
from PIL import Image
import numpy as np
from streamlit_option_menu import option_menu

def image_details(input_image):
  inputImage=Image.open(input_image)
  image_array=np.array(inputImage)
  reader=easyocr.Reader(["en"])
  text=reader.readtext(image_array,detail=0)
  return inputImage,text

def image_data(text):
  extracted_text={"name":[],"designation":[],"company name":[],"state":[],"web_site":[],"phone":[],"email":[],"address":[],"pincode":[]}
  extracted_text["name"].append(text[0])
  extracted_text["designation"].append(text[1])
  for i in range(2,len(text)):
    if text[i].startswith("+") or ("-")in text[i]:
      extracted_text["phone"].append(text[i])
    elif "@" in text[i] and text[i].endswith(".com"):
      lower=text[i].lower()
      remove_colon=re.sub(';,',' ',lower)
      extracted_text["email"].append(remove_colon)
    elif len(text[i])==6 and text[i].isdigit():
      extracted_text["pincode"].append(text[i])
    elif text[i].lower().startswith("www") and text[i].endswith(".com")or text[i].endswith("com") or (text[i].endswith(".com")):
      lower=text[i].lower()
      remove_colon=re.sub(';,',' ',lower)
      extracted_text["web_site"].append(remove_colon)
    elif "tamilnadu" in text[i].lower() or "tamil nadu" in text[i].lower() :
      extracted_text["state"].append(text[i])
    elif re.match(r'^[A-Za-z]',text[i]):
      lower=text[i].lower()
      remove_colon=re.sub(';,',' ',lower)
      extracted_text["company name"].append(remove_colon)

    else:
      remove_colon1=re.sub(';,',' ',text[i])
      extracted_text["address"].append(remove_colon1)

  for key,value in extracted_text.items():
    if len(value)>0:
      join=" ".join(value)
      extracted_text[key]=[join]
    else:
      value="NaN"
      extracted_text[key]=[value]
  return  extracted_text

#streamlit part
st.set_page_config(layout="wide")
st.title("bizcard data extraction using easy ocr")

with st.sidebar:
  options=option_menu("main menu",["home","extract and save","delete"])
if options=="home":
  st.image("/content/optical-character-recognition.jpg")
  st.markdown("### :blue[**Technologies Used :**] Python, easy OCR, Streamlit, PostgreSQL, Pandas")
  st.write("### :green[**About :**] Bizcard is a Python application designed to extract information from business cards.")
  st.write("### The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.")
  col1,col2=st.columns(2)
  with col1:
    st.title("EasyOCR FACTS")
    st.write("### 1.Lightweight and User-Friendly")
    st.write("### 2.Multiple Language Support")
    st.write("### 3.Pre-Trained Models")
    st.write("### 3.Open-Source and Actively Developed")
    st.write("### 4.Wide Range of Applications")
    st.write("### 5.Continuous Improvements")
  with col2:
    st.title("HOW OCR WORKS")
    st.video("/content/What is Optical Character Recognition (OCR)_ and how does it work_.mp4")
  st.write("### :red[**Challenges :**] Despite advancements, OCR can still struggle with low-quality images, handwritten text, and complex layouts")

elif options=="extract and save":
  st.image("/content/ocr.jpg")
  col1,col2=st.columns(2)
  with col1:
    image=st.file_uploader("upload your image",type=["png","jpg","jpng"])
  if image:
    inputImage,text=image_details(image)
    with col2:
      st.image(image,width=425)

    inputImage,text=image_details(image)
    text_data=image_data(text)

    if text:
      st.success("text extracted successfully")

    image_bytes=io.BytesIO()
    inputImage.save(image_bytes,format="PNG")
    image_data=image_bytes.getvalue()
    image_bites_data={"IMAGE":[image_data]}
    df=pd.DataFrame(text_data)
    df1=pd.DataFrame(image_bites_data)
    final_data=pd.concat([df,df1],axis=1)
    st.dataframe(final_data)

    if text:
      save_button=st.button("save",use_container_width=True)
      if save_button:
        mydb=sqlite3.connect("bizcard_new.db")
        cursor=mydb.cursor()
        #creating the table
        create_querry='''CREATE TABLE IF NOT EXISTS BIZCARD_NEW_DETAILS (name varchar(20),
                                                                    designation varchar(20),
                                                                    company_name varchar(20),
                                                                    state varchar(20),
                                                                    web_site varchar(20),
                                                                    phone int,
                                                                    email varchar(20),
                                                                    address varchar(20),
                                                                    pincode varchar(20),
                                                                    image text PRIMARY KEY)'''

        cursor.execute(create_querry)
        mydb.commit()

        #inserting values

        try:
          insert_querry='''INSERT INTO BIZCARD_NEW_DETAILS (name,designation,company_name,state,web_site,phone,email,address,pincode,image)
                                  VALUES(?,?,?,?,?,?,?,?,?,?)
                                                      '''
          datas= final_data.values.tolist()
          cursor.executemany(insert_querry,datas)
          mydb.commit()
          st.success("saved successfully")
        except:
          st.success("booooo")

  tab1,tab2=st.tabs(["preview","modify"])
  with tab1 :
    mydb=sqlite3.connect("bizcard_new.db")
    cursor=mydb.cursor()
    try:
      query = '''SELECT * FROM BIZCARD_NEW_DETAILS'''

      cursor.execute(query)

      table = cursor.fetchall()
      mydb.commit()
      df2 = pd.DataFrame(table, columns=("name", "designation", "company_name", "state", "web_site", "phone", "email", "address", "pincode", "image"))
      data=st.dataframe(df2)
    except :
      st.warning(" Please upload an image and extract the text and save it to view")



  with tab2:
    try:
      mydb=sqlite3.connect("bizcard_new.db")
      cursor=mydb.cursor()
      querry='''SELECT * FROM BIZCARD_NEW_DETAILS'''
      cursor.execute(querry)
      table=cursor.fetchall()
      mydb.commit()
      df2=pd.DataFrame(table,columns=("name","designation","company_name","state","web_site","phone","email","address","pincode","image"))
      select_name=st.selectbox("select the name",df2["name"])
      df3=df2[df2["name"]==select_name]
      df4=df3.copy()
      st.write(f"information of {select_name}")
      st.dataframe(df3)
      col1,col2=st.columns(2)
      with col1:
        mo_name=st.text_input("name",df3["name"].unique()[0])
        mo_designation=st.text_input("designation",df3["designation"].unique()[0])
        mo_company_name=st.text_input("company_name",df3["company_name"].unique()[0])
        mo_state=st.text_input("state",df3["state"].unique()[0])
        mo_web_site=st.text_input("web_site",df3["web_site"].unique()[0])

        df4["name"]=mo_name
        df4["designation"]=mo_designation
        df4["company_name"]=mo_company_name
        df4["state"]=mo_state
        df4["web_site"]=mo_web_site

      with col2:
        mo_phone=st.text_input("phone",df3["phone"].unique()[0])
        mo_email=st.text_input("email",df3["email"].unique()[0])
        mo_address=st.text_input("address",df3["address"].unique()[0])
        mo_pincode=st.text_input("pincode",df3["pincode"].unique()[0])
        mo_image=st.text_input("image",df3["image"].unique()[0])
        df4["phone"]=mo_phone
        df4["email"]=mo_email
        df4["address"]=mo_address
        df4["pincode"]=mo_pincode
        df4["image"]=mo_image

      st.write(f"updated information of {select_name}")
      st.dataframe(df4)
    except:
      st.warning("The table does not exist in the database. Please upload an image and extract the text")
    save_button=st.button("update",use_container_width=True)
    if save_button:
      mydb=sqlite3.connect("bizcard_new.db")
      cursor=mydb.cursor()
      cursor.execute(f"DELETE FROM BIZCARD_NEW_DETAILS WHERE name='{select_name}'")
      mydb.commit()
      #inserting values
      insert_querry='''INSERT INTO BIZCARD_NEW_DETAILS (name,designation,company_name,state,web_site,phone,email,address,pincode,image)
                              VALUES(?,?,?,?,?,?,?,?,?,?)
                                                    '''
      datas= df4.values.tolist()
      cursor.executemany(insert_querry,datas)
      mydb.commit()
      st.success("updated successfully")
elif options=="delete":
  try:
    mydb=sqlite3.connect("bizcard_new.db")
    cursor=mydb.cursor()
    querry='''SELECT * FROM BIZCARD_NEW_DETAILS'''
    cursor.execute(querry)
    table=cursor.fetchall()
    mydb.commit()
    df2=pd.DataFrame(table,columns=("name","designation","company_name","state","web_site","phone","email","address","pincode","image"))
    select_name=st.selectbox("select the name",df2["name"])
    delet_data=df2[df2["name"]==select_name]
    st.write(f"information of'{select_name}'")
    st.dataframe(delet_data)
    delete=st.button("delete",use_container_width=True)
    st.image("/content/Delete Button.png")
    if delete:
      querry=(f"DELETE FROM BIZCARD_NEW_DETAILS WHERE name='{select_name}'")
      cursor.execute(querry)
      mydb.commit()
      st.success("deleted successfully")
  except:
    st.warning("!!NO DATA TO DISPLAY!! please extract some text and save it ")
