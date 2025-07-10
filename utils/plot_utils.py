import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def line_plot(df: pd.DataFrame, x_axis: str, y_axis: str) -> plt.Figure:
    """
    Создает линейный график. Этот график отображает зависимость значений по оси Y от значений по оси X,
    представляя временную динамику или тенденцию данных.

    args:
        df: DataFrame, содержащий данные для построения графика.
            Должен содержать столбцы, указанные в x_axis и y_axis.
        x_axis: Название столбца из DataFrame, который будет использоваться
                для оси абсцисс (ось X). Обычно это временные ряды или категории.
        y_axis: Название столбца из DataFrame, который будет использоваться
                для оси ординат (ось Y). Представляет значения, которые
                отображаются в зависимости от оси X.

    returns:
        plt.Figure: Объект Figure Matplotlib, представляющий созданный линейный график.
    """
    plt.figure(figsize=(10, 8))
    sns.lineplot(x=x_axis, y=y_axis, data=df)
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.title(f"Динамика {y_axis} по {x_axis}")
    plt.grid(True)
    return plt.gcf()


def bar_plot(df: pd.DataFrame, x_axis: str, y_axis: str) -> plt.Figure:
    """
    Создает и возвращает столбчатую диаграмму. Этот график используется для сравнения 
    значений между категориями.

    Args:
        df: DataFrame, содержащий данные для построения графика.
            Должен содержать столбцы, указанные в x_axis и y_axis.
        x_axis: Название столбца из DataFrame, который будет использоваться
                для оси абсцисс (ось X). Представляет категории для сравнения.
        y_axis: Название столбца из DataFrame, который будет использоваться
                для оси ординат (ось Y). Представляет количественное значение,
                соответствующее каждой категории на оси X.

    Returns:
        plt.Figure: Объект Figure Matplotlib, представляющий созданную столбчатую диаграмму.
    """
    plt.figure(figsize=(10, 8))
    sns.barplot(x=x_axis, y=y_axis, data=df)
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.title(f"Соотношение {y_axis} по {x_axis}")
    plt.grid(True)
    return plt.gcf()


def hist_plot(df: pd.DataFrame, x_axis: str, y_axis: str = None) -> plt.Figure:
    """
    Создает и возвращает гистограмму (histogram) или группированную гистограмму.

    Гистограмма визуализирует распределение числовых данных.
    - Если y_axis не указан, строится гистограмма для столбца x_axis.
    - Если y_axis указан, строится гистограмма для столбца y_axis, с разделением
      по категориям, определенным в столбце x_axis.

    Args:
        df: DataFrame, содержащий данные для построения графика.
            Должен содержать столбцы, указанные в x_axis и/или y_axis.
        x_axis: Название столбца из DataFrame. Если y_axis не указан, это столбец
                для гистограммы. Если y_axis указан, это столбец, содержащий
                категории для группировки.
        y_axis: Название столбца из DataFrame для построения гистограммы
                (значения на оси Y). Если None, используется x_axis.
                По умолчанию None.

    Returns:
        plt.Figure: Объект Figure Matplotlib, представляющий созданную гистограмму.
    """
    plt.figure(figsize=(10, 8))
    if y_axis is None:
        sns.histplot(x=x_axis, data=df, bins=30)
        plt.title(f"Распределение {x_axis}")
    else:
        for category in df[y_axis].unique():
            subset = df[df[y_axis] == category]
            sns.histplot(x=x_axis, data=subset, kde=True, label=category, bins=30)
            plt.title(f"Распределение {x_axis} по {y_axis}")
        plt.xlabel(f"{y_axis}")
        plt.ylabel("Frequency")
        plt.legend()
    plt.grid(True)
    return plt.gcf()


def box_plot(df: pd.DataFrame, x_axis: str, y_axis: str) -> plt.Figure:
    """
    Создает и возвращает ящик с усами (box plot).
    
    Args:
        df: DataFrame, содержащий данные для построения графика.
            Должен содержать столбцы, указанные в x_axis и y_axis.
        x_axis: Название столбца из DataFrame, который будет использоваться
            для оси абсцисс (ось X). Представляет категории, по которым
            анализируется распределение.
        y_axis: Название столбца из DataFrame, который будет использоваться
            для оси ординат (ось Y). Представляет числовые значения,
            распределение которых нужно визуализировать для каждой категории.

    Returns:
        plt.Figure: Объект Figure Matplotlib, представляющий созданный ящик с усами.
    """
    plt.figure(figsize=(10, 8))
    sns.boxplot(x=x_axis, y=y_axis, data=df)
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.title(f"Распределение {y_axis} по {x_axis}")
    plt.grid(True)
    plt.suptitle("")
    return plt.gcf()


def pie_plot(df: pd.DataFrame, x_axis: str, y_axis: str) -> plt.Figure:
    """
    Создает круговую диаграмму. Отображает доли (проценты) различных категорий в общем объеме.
    Args:
        df: DataFrame, содержащий данные для построения графика.
            Должен содержать столбцы, указанные в x_axis и y_axis.
        x_axis: Название столбца из DataFrame, который будет использоваться
                для меток долей (например, названия товаров).
        y_axis: Название столбца из DataFrame, который будет использоваться
                для значений долей (например, суммы продаж).
    Returns:
        plt.Figure: Объект Figure Matplotlib, представляющий созданную круговую диаграмму.
    """
    plt.figure(figsize=(8, 8))
    plt.pie(df[y_axis], labels=df[x_axis], autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    plt.title(f"Доли {y_axis} по {x_axis}")
    plt.axis('equal')
    plt.tight_layout()
    return plt.gcf()
