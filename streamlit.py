import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_option('deprecation.showPyplotGlobalUse', False)

# Заголовок
st.title('Hi! Это мой финальный проект по курсу Start in DS от магистратуры Искусственный Интеллект факультета компьтерных наук ВШЭ')
# подзаголовок - проект
st.header('Проект: анализ зарплат в России')
# подподзаголовок о чем проект
st.markdown('''
В проекте мы будем пользоваться открытыми данными из официальных источников:
            
[Сайт Росстата]('https://rosstat.gov.ru/')
             
[Таблицы уровня инфляции в России]('https://уровень-инфляции.рф/')
             
Предлагается проанализировать динамику уровня средних зарплат в разрезе по видам экономической деятельности за последние 30 лет в России.''')

# загрузка данных инфляции
# file = st.file_uploader('загрузите данные инфляции', type='xlsx')
file = 'inflation.xlsx'

if file:
    inf = pd.read_excel(file, header=None, index_col=0)
    inf.index.name = 'years'
    inf.columns = ['inf']
    try:
        st.write('Данные инфляции с 2000 года по 2023 ')
        inf.T
    except:
        st.write('что-то пошло не так')


# загрузка данных по экономическим деятельностям
# econom = st.file_uploader('загрузите данные по экономическим деятельностям', type='xlsx')
econom = 'tab3-zpl_2023.xlsx'

if econom:
    # загрузка и обработка первого листа 
    data1 = pd.read_excel(econom, sheet_name=0)
    data1.columns = ['types', '2017', '2018', '2019', '2020', '2021', '2022', '2023']
    data1 = data1.drop([0,1,2,3,57,58,59])
    for i in data1.index:
        data1['types'][i] = data1['types'][i].lower()

    # загрузка и обработка второго листа
    data2 = pd.read_excel(econom, sheet_name=1)
    data2.columns = ['types'] + [str(i) for i in range(2000, 2017)]
    data2 = data2.drop([0,1,37,38])
    for i in data2.index:
        data2['types'][i] = data2['types'][i].lower()

    data_1 = data1.loc[[43,46,54]]
    data_1['types'][46] = data2['types'][28]
    data_1.index = [0,1,2]

    data_2 = data2.loc[[26,28,34]]
    data_2.index = [0,1,2] 

    # объединяем две части по данных по нашим сферам
    salaries = data_2.merge(data_1)
    salaries.index = salaries['types'].values
    salaries.drop('types', axis=1, inplace=True)
    salaries = salaries.astype('float64')
    try:
        st.write('Средние зарплаты по экономическим деятельностям')
        st.dataframe(salaries)
    except:
        st.write('что-то пошло не так')

    st.write('посмотрим на график изменения зарплат')

    # строю графики изменения зарплат 
    plt.figure(figsize=[16,9])
    plt.plot(salaries.columns, salaries.iloc[0].values, color='green', marker='.', markersize=8)
    plt.plot(salaries.columns, salaries.iloc[1].values, color='black', marker='.', markersize=8)
    plt.plot(salaries.columns, salaries.iloc[2].values, color='red', marker='.', markersize=8)
    plt.title('график изменения зарплат по годам в сферах: строительство, гостиницы и рестораны, образование')
    plt.xlabel('года')
    plt.ylabel('зарплата, рублей')
    plt.legend(salaries.index)
    st.pyplot()

    st.write('''Выводы: Выросли все рассмотреные экономические деятельности,
              сильнее всего выросла деятельность строительство, меньше всего гостиницы и рестораны.
              Хорошо показывает себя деятельность образование.''')


    # средние зарплаты с учётом уровня инфляции
    salaries_with_inflation = (salaries * (1 - inf['inf'].values/100)).round(2)
    

    # строю графики изменения зарплат 
    plt.figure(figsize=[16,9])
    plt.plot(salaries.columns, salaries.iloc[0].values, color='green', marker='.', markersize=8, linewidth=3)
    plt.plot(salaries_with_inflation.columns, salaries_with_inflation.iloc[0].values, color='green', marker='.', markersize=5, alpha=0.5)
    plt.plot(salaries.columns, salaries.iloc[1].values, color='black', marker='.', markersize=8, linewidth=3)
    plt.plot(salaries_with_inflation.columns, salaries_with_inflation.iloc[1].values, color='black', marker='.', markersize=5, alpha=0.5)
    plt.plot(salaries.columns, salaries.iloc[2].values, color='red', marker='.', markersize=8, linewidth=3)
    plt.plot(salaries_with_inflation.columns, salaries_with_inflation.iloc[2].values, color='red', marker='.', markersize=5, alpha=0.5)
    plt.title('график изменения зарплат без и с учетом инфляции по годам в сферах: строительство, гостиницы и рестораны, образование')
    plt.xlabel('года')
    plt.ylabel('зарплата, рублей')
    plt.legend(['строительство', 'строительство с учетом инфляции', "гостиницы и рестораны", "гостиницы и рестораны с учетом инфляции",
                "образование", "образование с учетом инфляции"])
    st.pyplot()


    # номинальный рост средних зарплат
    salary_growth = salaries.diff(axis=1).fillna(0)
    salary_growth

    # насколько должна была быть выше зарплата с учетом инфляции
    salar_inf = (salaries * (inf['inf'].values/100)).round(2)
    salar_inf

    # рост зарплат с поправкой на инфляцию
    salary_growth_with_inflation = salary_growth.sub(salar_inf.shift(axis=1), axis=1, fill_value=0)
    salary_growth_with_inflation

    # график роста зарплат с учетом инфляции
    plt.figure(figsize=[13,8])
    plt.axhline(y=0, color='blue', linestyle='--')
    plt.plot(salary_growth_with_inflation.columns, salary_growth_with_inflation.iloc[0].values, color='green', marker='.', markersize=8)
    plt.plot(salary_growth_with_inflation.columns, salary_growth_with_inflation.iloc[1].values, color='black', marker='.', markersize=8)
    plt.plot(salary_growth_with_inflation.columns, salary_growth_with_inflation.iloc[2].values, color='red', marker='.', markersize=8)
    plt.title('рост зарплат с учетом инфляции')
    plt.xlabel('года')
    plt.ylabel('зарплата, рублей')
    plt.legend(['отметка ноль','строительство','гостиницы и рестораны','образование'])
    st.pyplot()


    # график роста зарплат без и с учета инфляции
    plt.figure(figsize=[13,8])
    plt.axhline(y=0, color='blue', linestyle='--')
    plt.plot(salary_growth_with_inflation.columns, salary_growth_with_inflation.iloc[0].values, color='green', marker='.', markersize=8, linewidth=3)
    plt.plot(salary_growth.columns, salary_growth.iloc[0].values, color='green', marker='.', markersize=5, alpha=0.5)
    plt.plot(salary_growth_with_inflation.columns, salary_growth_with_inflation.iloc[1].values, color='black', marker='.', markersize=8, linewidth=3)
    plt.plot(salary_growth.columns, salary_growth.iloc[1].values, color='black', marker='.', markersize=5, alpha=0.5)
    plt.plot(salary_growth_with_inflation.columns, salary_growth_with_inflation.iloc[2].values, color='red', marker='.', markersize=8, linewidth=3)
    plt.plot(salary_growth.columns, salary_growth.iloc[2].values, color='red', marker='.', markersize=5, alpha=0.5)
    plt.xlabel('года')
    plt.ylabel('зарплата, рублей')
    plt.legend(['отметка ноль',
                'сфера строительство с учетом инфляции', 'сфера строительство без учета инфляции',
                'сфера гостиницы и рестораны с инфляцией', 'сфера гостиницы и рестораны без инфляции',
                'сфера образование с инфляцией', 'сфера образование без инфляции'])
    plt.title('рост зарплат без и с учетом инфляции')
    st.pyplot()

    st.write('''
                Выводы: С учетом инфляции рост зарплат по всем сферам не такой радужный как могло показаться.
                 Часто рост зарплат уходит в 'минус'. Наблюдаем большие разрывы между ростом без инфляции и с инфляией.''')