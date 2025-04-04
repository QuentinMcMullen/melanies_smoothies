# Import python packages
import streamlit as st
###from snowflake.snowpark.context import get_active_session  #needed for streamlit in snowflake, but not needed for pure streamlit
from snowflake.snowpark.functions import col
import requests
import pandas as pd


# Write directly to the app
st.title(":cup_with_straw: Smoothies! :smile:")
st.write("Choose your fruit.:")


# option = st.selectbox(
#     "What is your favorite fruit?",
#     ("Banana", "Strawberries", "Peaches"),
#     index=None,
#     placeholder="Select Fruit...",
# )


# st.write("Your favorite fruit:", option)

name_on_order=st.text_input('Name on Smoothie:')
st.write('The name on your smoothie will be:',name_on_order)





###session = get_active_session() #for streamlit in snowflake

cnx=st.connection("snowflake")  #for streamlit NOT in snowflake
session = cnx.session() 



my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_Name'),col('Search_on'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#my_dataframe is a streamlit data frame.  Make a pandas dataframe so can use iloc

pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()




ingredients_list=st.multiselect('Choose up to 5 ingredients'
                                , my_dataframe
                               ,max_selections=5)

if ingredients_list:
    #st.write(ingredients_list)
    #st.text(ingredients_list)

    ingredients_string=''
    for fruit_chosen in ingredients_list:
        ingredients_string+=fruit_chosen+ " "

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df=st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)


    st.write("You chose: " + ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
                values ('""" + ingredients_string + """'
                       ,'""" + name_on_order + """'
                        )"""
    
    st.write(my_insert_stmt)

    time_to_insert=st.button("Submit Order")

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered, ' + name_on_order + '!', icon="✅")




