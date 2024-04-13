import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# настраиваем конфиг страницы
st.set_page_config(page_title='Анализ зарплат в России', page_icon='📊', layout="wide")

# убираем предупреждения при постороении графиков
st.set_option('deprecation.showPyplotGlobalUse', False)


# прописываем пути
data_folder = Path('data/')
absolute_path_inf = data_folder / 'inflation.xlsx'
absolute_path_data = data_folder / 'tab3-zpl_2023.xlsx'

# Заголовок
st.title('Hi! Это мой финальный проект по курсу Start in DS от магистратуры Искусственный Интеллект факультета компьютерных наук ВШЭ')

# подзаголовок - проект
st.header('Проект: анализ зарплат в России')

# подподзаголовок о чем проект
st.markdown('''
В проекте мы будем пользоваться открытыми данными из официальных источников:
            
[Сайт Росстата](https://rosstat.gov.ru/)
             
[Таблицы уровня инфляции в России](https://уровень-инфляции.рф/)
             
Предлагается проанализировать динамику уровня средних зарплат в разрезе по видам экономической деятельности с 2000 года в России.''')

st.markdown('---')

# загрузка данных инфляции
# file = st.file_uploader('загрузите данные инфляции', type='xlsx')
file = absolute_path_inf

@st.cache_data
def load_inf():
    inf = pd.read_excel(file, header=None, index_col=0)
    inf.index.name = 'years'
    inf.columns = ['inf']
    return inf

if file:
    inf = load_inf()
    st.write('Данные инфляции с 2000 года по 2023 ')
    inf.T


# загрузка данных по экономическим деятельностям
# econom = st.file_uploader('загрузите данные по экономическим деятельностям', type='xlsx')
econom = absolute_path_data

@st.cache_data
def load_econom():
    # Загрузка и обработка первого листа данных
    data1 = pd.read_excel(econom, sheet_name=0)
    data1.columns = ['types', '2017', '2018', '2019', '2020', '2021', '2022', '2023']
    data1 = data1.drop([0,1,2,3,57,58,59])
    for i in data1.index:
        data1['types'][i] = data1['types'][i].lower()
    data_1 = data1.loc[[43,46,54]]
    data_1['types'][46] = 'гостиницы и рестораны'
    data_1.index = [0,1,2]

    # загрузка и обработка второго листа данных
    data2 = pd.read_excel(econom, sheet_name=1)
    data2.columns = ['types'] + [str(i) for i in range(2000, 2017)]
    data2 = data2.drop([0,1,37,38])
    for i in data2.index:
        data2['types'][i] = data2['types'][i].lower()
    data_2 = data2.loc[[26,28,34]]
    data_2.index = [0,1,2] 

    # объединение данных
    salaries = data_2.merge(data_1) 
    salaries.index = salaries['types'].values
    salaries.drop('types', axis=1, inplace=True)
    salaries = salaries.astype('float64')
    return salaries

if econom:
    salaries = load_econom()

    # функция вывода данных в зависимости от выбора
    @st.cache_data
    def print_out_df(df, logic):
        return df.loc[logic]

    # функция отрисовки графика роста зарплат
    # @st.cache_data
    def draw_salary_growth(types):
        st.write('Посмотрим на график роста зарплат')
        plt.figure(figsize=[16,9])
        plt.grid()
        colors=['green', 'black', 'red']
        leg = []
        for i, v in enumerate(types):
            if v == True:
                plt.plot(salaries.columns, salaries.iloc[i].values, color=colors[i], marker='.', markersize=8)
                leg.append(salaries.iloc[i].name)
        plt.title(f'Рост зарплат по годам в сферах: {", ".join(leg)}')
        plt.xlabel('года')
        plt.ylabel('зарплата, рублей')
        plt.legend(leg)
        st.pyplot()
        st.write('''Выводы: Выросли все рассмотреные экономические деятельности,
              сильнее всего выросла деятельность строительство, меньше всего гостиницы и рестораны.
              Хорошо показывает себя деятельность образование. Рост номинальных зарплат имеет положительный тренд''')
        st.markdown('---')
        

    # функция подсчёта зарплат с учетом инфляции
    @st.cache_data
    def salaries_with_inf():
        return (salaries * (1 - inf['inf'].values/100)).round(2)
    
    salaries_with_inflation = salaries_with_inf()


    # функция отрисовки сравнения графиков роста зарплат без и с учетом инфляции
    # @st.cache_data
    def draw_salary_growth_with_inf(types):
        st.write('Посмотрим на сравнение графиков роста зарплат без и с учетом инфляции')
        plt.figure(figsize=[16,9])
        plt.grid()
        colors=['green', 'black', 'red']
        leg = []
        names = set()
        for i, v in enumerate(types):
            if v == True:
                plt.plot(salaries.columns, salaries.iloc[i].values, color=colors[i], marker='.', markersize=8)
                plt.plot(salaries_with_inflation.columns, salaries_with_inflation.iloc[i].values,
                          color=colors[i], marker='.', markersize=5, alpha=0.5)
                names.add(salaries.iloc[i].name)
                leg.append(salaries.iloc[i].name)
                leg.append(salaries_with_inflation.iloc[i].name + " с инфляцией")
        plt.title(f'''сравнение роста зарплат без и с учетом инфляции по годам в сферах:
                   {", ".join(names)}''')
        plt.xlabel('года')
        plt.ylabel('зарплата, рублей')
        plt.legend(leg)
        st.pyplot()


    # функция отрисовки изменения зарплат без и с учётом инфляции
    def draw_changes_with_inf_without(types):
        st.write('Сравнение изменениий номинальных зарплат и реальных зарплат с учётом инфляции')
        plt.figure(figsize=[16,9])
        plt.grid()
        colors=['green', 'black', 'red']
        leg = []
        names = set()
        for i, v in enumerate(types):
            if v == True:
                plt.plot(salary_changes_with_inflation.columns, salary_changes_with_inflation.iloc[i].values,
                        color=colors[i], marker='.', markersize=8)
                plt.plot(salary_growth.columns, salary_growth.iloc[i].values, color=colors[i], marker='.', markersize=5, alpha=0.5)
                names.add(salaries.iloc[i].name)
                leg.append(salary_changes_with_inflation.iloc[i].name + " с инфляцией")
                leg.append(salary_growth.iloc[i].name + ' без инфляции')
        plt.title(f'''Сравнение изменений зарплат с учётом инфляции и без по годам в сферах: 
                  {", ".join(names)}''')
        plt.xlabel('года')
        plt.ylabel('зарплата, рублей')
        plt.legend(leg)
        st.pyplot()


    # функция подсчета номинального роста средних зарплат
    @st.cache_data
    def salary_growth():
        return salaries.diff(axis=1).fillna(0)
    
    salary_growth = salary_growth()


    # сколько недополучили люди из-за инфляции
    @st.cache_data
    def salar_inf():
        return (salaries * (inf['inf'].values/100)).round(2)

    salar_inf = salar_inf()


    # функция подсчёта изменения зарплаты с поправкой на инфляцию
    @st.cache_data
    def salary_changes_with_inflation():
        return salary_growth.sub(salar_inf.shift(axis=1), axis=1, fill_value=0)
    
    salary_changes_with_inflation = salary_changes_with_inflation()


    # функция отрисовки графика изменения зарплат с инфляцией
    def draw_salary_changes_with_inf(types):
            st.write('Динамика изменений реальных зарплат с учётом инфляции')
            plt.figure(figsize=[16,9])
            plt.grid()
            colors=['green', 'black', 'red']
            leg = []
            for i, v in enumerate(types):
                if v == True:
                    plt.plot(salary_changes_with_inflation.columns, salary_changes_with_inflation.iloc[i].values,
                            color=colors[i], marker='.', markersize=8)
                    leg.append(salaries.iloc[i].name)
            plt.title(f'Изменения зарплат с учётом инфляции по годам в сферах: {", ".join(leg)}')
            plt.xlabel('года')
            plt.ylabel('зарплата, рублей')
            plt.legend(leg)
            st.pyplot()

    # график столбчатый изменения зарплат с инфляцией и без
    @st.cache_data
    def draw_bar(i):
        plt.figure(figsize=[13,8])
        plt.yticks(np.arange(-3000, 10000, step=500))
        plt.grid()
        plt.bar(salary_changes_with_inflation.columns, salary_changes_with_inflation.iloc[i].values, color='green', alpha=0.5)
        plt.bar(salary_growth.columns, salary_growth.iloc[i].values, color='m', alpha=0.5)
        plt.title(f'изменения зарплат сферы {salary_changes_with_inflation.iloc[i].name} без и с учетом инфляции')
        plt.xlabel('года')
        plt.ylabel('изменение зарплаты, рублей')
        plt.legend(['с учетом инфляции','без учета инфляции'])
        st.pyplot()

    @st.cache_data
    def create_tabs():
        tab1, tab2, tab3 = st.tabs(['Строительство', 'Гостиницы и рестораны', 'Образование'])
        with tab1:
            st.header('Строительство')
            draw_bar(0)
        with tab2:
            st.header('Гостиницы и рестораны')
            draw_bar(1)
        with tab3:
            st.header('Образование')
            draw_bar(2)

    @st.cache_data
    def main_fun(types):
        st.write('Номинальные средние зарплаты по экономическим деятельностям')
        st.dataframe(print_out_df(salaries, types).style.format('{:.2f}'))
        draw_salary_growth(types)
        st.write('Реальные средние зарплаты с учётом уровня инфляции')
        st.dataframe(print_out_df(salaries_with_inf(), types).style.format('{:.2f}'))
        draw_salary_growth_with_inf(types)
        st.write('Номинальное изменение зарплат')
        st.dataframe(print_out_df(salary_growth, types).style.format('{:.2f}'))
        st.write('Динамика изменений реальных зарплат с учетом инфляции')
        st.dataframe(print_out_df(salary_changes_with_inflation, types).style.format('{:.2f}'))
        draw_salary_changes_with_inf(types)
        # st.write('Сравнение изменений без и с инфляцией')
        draw_changes_with_inf_without(types)

        st.write('Каждая сфера в другом виде')

        create_tabs()

        st.write('''
                Выводы: С учетом инфляции рост зарплат по всем сферам не такой радужный как могло показаться.
                  Часто рост зарплат уходит в 'минус'. Наблюдаем большие разрывы между ростом без инфляции и с инфляией.
                  Видим что в периоды 2008 - 2009, 2014 - 2016, 2018 - 2019, 2021 - 2023 года
                  практически все сферы имели отрицательную динамику изменений реальных зарплат.
                  В 2009 году сильнее всего постарадала сфера строительство.
                 ''')



    # sidebar панель слева
    with st.sidebar:
        st.sidebar.title('Выбор экономической деятельности для рассмотрения')
        stroi = st.checkbox('Строительство', True)
        rest = st.checkbox('Гостиницы и рестораны', True)
        learning = st.checkbox('Образование', True)

    types = [stroi, rest, learning]


    # строительство
    if stroi == True and rest == False and learning == False:
        main_fun(types)

    # гостиницы и рестораны
    if rest == True and stroi == False and learning == False:
        main_fun(types)

    # образование
    if learning == True and rest == False and stroi == False:
        main_fun(types)

    # образование и строительство
    if learning == True and stroi == True and rest == False:
        main_fun(types)

    # образование и гостиницы 
    if learning == True and rest == True and stroi == False:
        main_fun(types)
      
    #гостиницы и строительство
    if rest == True and stroi == True and learning == False:
        main_fun(types)

    # всё
    if learning == True and stroi == True and rest == True:
        main_fun(types)
    
    # ничего
    if learning == False and stroi == False and rest == False:
        st.error('Выберите хотя бы одну сферу !')
