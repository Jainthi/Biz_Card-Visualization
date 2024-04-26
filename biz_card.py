%%writefile biz.py

import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import sqlite3

def image_to_text(path):

  input=Image.open(path)
  #converting image to array format
  image_arr=np.array(input)

  reader=easyocr.Reader(['en'])
  text=reader.readtext(image_arr,detail=0)

  return text, input

def extracted_text(texts):

  extracted_dict={"Name":[],"Designation":[], "Company_Name":[], "Contact":[], "E_Mail":[],
                  "Website":[], "Address":[], "Pincode":[]}
  extracted_dict["Name"].append(texts[0])
  extracted_dict["Designation"].append(texts[1])

  for i in range(2,len(texts)):
    if texts[i].startswith("+") or (texts[i].replace("-", "").isdigit() and '-'in texts[i]):
      extracted_dict["Contact"].append(texts[i])

    elif "@" in texts[i] and ".com" in texts[i]:
      extracted_dict["E_Mail"].append(texts[i])

    elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
      extracted_dict["Website"].append(texts[i].lower())

    elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
      extracted_dict["Pincode"].append(texts[i])

    elif re.match(r'^[a-zA-Z]',texts[i]):
      extracted_dict["Company_Name"].append(texts[i])

    else:
      remove_colon=re.sub(r'[,;]','', texts[i])
      extracted_dict["Address"].append(remove_colon)

  for key,value in extracted_dict.items():
    if len(value)>0:
      concadenate=" ".join(value)
      extracted_dict[key] =[concadenate]

    else:
      value="NA"
      extracted_dict[key]=[value]

  return extracted_dict

#streamlit
st.set_page_config(layout="wide")
st.title("Extracting Business Card with Easy OCR")
st.set_page_config(layout="wide")
st.title("Extracting Business Card with Easy OCR")
selected = option_menu(None, ["Home","upload and modify","Delete Table"], 
                       icons=["house","cloud-upload","pencil-square"],
                       default_index=0,
                       orientation="horizontal",
                       styles={"nav-link": {"font-size": "35px", "text-align": "centre", "margin": "0px", "--hover-color": "#6495ED"},
                               "icon": {"font-size": "35px"},
                               "container" : {"max-width": "6000px"},
                               "nav-link-selected": {"background-color": "#6495ED"}})

if selected=="Home":
   
   col1,col2=st.columns(2)
   with col1:
    st.markdown("#### :green[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")
    st.markdown("#### :green[**Overview :**] In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the uploaded business card image. The database would be able to store multiple entries, each with its own business card image and extracted information.")
   with col2:
    st.image("b1.jpg")
    
elif selected=="upload and modify":
  img=st.file_uploader("Upload the Card", type=["png","jpg","jpeg"])

  if img is not None:
    st.image(img, width=300)

    text_image, input_img= image_to_text(img)

    text_dict= extracted_text(text_image)

    if text_dict:
      st.success("Text is extracted Successfully")

    df=pd.DataFrame(text_dict)

    #converting image to bytes

    Image_bytes=io.BytesIO()
    input_img.save(Image_bytes, format="png")

    img_data=Image_bytes.getvalue()
    #creating dict

    data={"Image":[img_data]}
    df_1=pd.DataFrame(data)

    concat_df=pd.concat([df,df_1],axis=1)

    st.dataframe(concat_df)
    button_1=st.button("Save")

    if button_1:
      mydb = sqlite3.connect("bizcardx.db")
      cursor = mydb.cursor()

      #Table creation

      create_querry='''Create Table if not exists bizcard_details(name varchar(225),
                                                            designation varchar(225),
                                                            company_name varchar(225),
                                                            contact_number varchar(225),
                                                            email varchar(225),
                                                            website text,
                                                            address text,
                                                            pincode varchar(225),
                                                            image text)'''
      cursor.execute(create_querry)
      mydb.commit()

      insert_querry='''insert into bizcard_details(name,designation,company_name,contact_number,
                                              email, website, address, pincode,image)

                                              values(?,?,?,?,?,?,?,?,?)'''
      datas= concat_df.values.tolist()[0]
      cursor.execute(insert_querry,datas)
      mydb.commit()
      st.success("Saved Successfully")

  method = st.radio("Select the Method",["None","Preview","Modify"])
  if method == "None":
    st.write("")
  if method == "Preview":
    mydb = sqlite3.connect("bizcardx.db")
    cursor = mydb.cursor()
    
    select_query="select * from bizcard_details"

    cursor.execute(select_query)
    table=cursor.fetchall()

    mydb.commit()

    table_df = pd.DataFrame(table, columns=("Name","Designation","Company Name","Contact Number","E-Mail","Website", "Address","Pincode","Image"))
    st.dataframe(table_df)

  elif method == "Modify":

    mydb = sqlite3.connect("bizcardx.db")
    cursor = mydb.cursor()
    
    select_query="select * from bizcard_details"

    cursor.execute(select_query)
    table=cursor.fetchall()

    mydb.commit()

    table_df = pd.DataFrame(table, columns=("Name","Designation","Company_Name","Contact_Number","E-Mail","Website", "Address","Pincode","Image"))

    col1,col2=st.columns(2)
    with col1:

      selected_name=st.selectbox("Select the Name", table_df["Name"])
    df_3=table_df[table_df["Name"] == selected_name]

    df_4=df_3.copy()

    col1,col2=st.columns(2)

    with col1:

      modify_name = st.text_input("Name", df_3["Name"].unique()[0])
      modify_desig = st.text_input("Designation", df_3["Designation"].unique()[0])
      modify_com_name = st.text_input("Company_Name", df_3["Company_Name"].unique()[0])
      modify_contact_number = st.text_input("Contact_Number", df_3["Contact_Number"].unique()[0])
      modify_email = st.text_input("E-Mail", df_3["E-Mail"].unique()[0])

      df_4["Name"]=modify_name
      df_4["Designation"]=modify_desig
      df_4["Company_Name"]=modify_com_name
      df_4["Contact_Number"]=modify_contact_number
      df_4["E-Mail"]=modify_email
      
    with col2:

      modify_web = st.text_input("Website", df_3["Website"].unique()[0])
      modify_add = st.text_input("Address", df_3["Address"].unique()[0])
      modify_pin = st.text_input("Pincode", df_3["Pincode"].unique()[0])
      modify_image = st.text_input("Image", df_3["Image"].unique()[0])

      df_4["Website"]=modify_web
      df_4["Address"]=modify_add
      df_4["Pincode"]=modify_pin
      df_4["Image"]=modify_image

    st.dataframe(df_4)

    col1,col2=st.columns(2)
    with col1:

      button_3=st.button("Modify",use_container_width=True)

    if button_3:

      mydb = sqlite3.connect("bizcardx.db")
      cursor = mydb.cursor()

      cursor.execute(f"delete from bizcard_details where Name ='{selected_name}'")
      mydb.commit()
       
      insert_querry='''insert into bizcard_details(name,designation,company_name,contact_number,
                                              email, website, address, pincode,image)

                                              values(?,?,?,?,?,?,?,?,?)'''
      datas= df_4.values.tolist()[0]
      cursor.execute(insert_querry,datas)
      mydb.commit()
      st.success("Modified Successfully")



elif selected=="Delete Table":
  mydb = sqlite3.connect("bizcardx.db")
  cursor = mydb.cursor()

  col1,col2=st.columns(2)
  with col1:
    select_query="select Name from bizcard_details"

    cursor.execute(select_query)
    table1=cursor.fetchall()

    mydb.commit()
    names=[]
    for i in table1:
      names.append(i[0])

    name_select=st.selectbox("Select the Name", names)

  with col2:
  
    select_query=f"select Designation from bizcard_details where name='{name_select}'"

    cursor.execute(select_query)
    table2=cursor.fetchall()

    mydb.commit()
    designations=[]
    for j in table2:
      designations.append(j[0])

    desig_select=st.selectbox("Select the Designation", designations)

    if name_select and desig_select:
      col1,col2,col3=st.columns(3)

      with col1:
        st.write(f"Selected Name :{name_select}")
        st.write("")
        st.write("")
        st.write("")
        st.write(f"Selected Designation : {desig_select}")

      with col2:

        st.write("")
        st.write("")
        st.write("")
        st.write("")
        remove=st.button("Delete", use_container_width=True)
        if remove:
          cursor.execute(f"delete from bizcard_details where Name='{name_select}'and Designation = '{desig_select}'")
          mydb.commit()
          st.warning("Deleted")
