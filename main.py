# Extras: 
    # Added Menu to select the analysis you wish to see
    # Error handling for main menu, if the user does not enter a number
    # Average car rating by car name
    # Average word count per rating


import pandas as df
from datetime import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import re


CAR_FILE = "cars_pa3.txt"
REVIEW_FILE = "reviews_pa3.txt"

df.set_option("display.max_colwidth", None)

def main():
    car_df = get_car_data()
    review_df = get_review_data()

    display_avg_word_count_per_rating(review_df)

    menu_options = [
        lambda: describe_col(review_df, "rating"),
        lambda: describe_col(review_df, "word_count"),
        lambda: display_rating_by_year(review_df),
        lambda: display_average_word_count(review_df),
        lambda: display_ratings_count_distribution(review_df),
        lambda: display_yearly_ratings_by_car_make(review_df, car_df),
        lambda: display_avg_rating_by_car(review_df),
        lambda: display_avg_word_count_per_rating(review_df)
    ]

    exit_option = len(menu_options) + 1

    choice = get_main_menu_choice()
    while choice != exit_option:
        menu_options[choice-1]()
        pause()
        choice = get_main_menu_choice()

def get_main_menu_choice():
    display_menu()
    try:
        num = int(input("\nPlease select one of the options above: "))
        return num
    except:
        print("Please enter a valid option")
        pause()
        return get_main_menu_choice()

def display_menu():
    menu_options = [
        "Review Rating Column",
        "Review Word Count Column",
        "Rating Count Distribution by Year",
        "Average Word Count by Year",
        "Ratings Count Distribution by Seasons and Years",
        "Average Yearly Ratings Distribution by Car Make",
        "Average Rating by Car",
        "Average Word Count by Rating"
        "Exit"
    ]
    for num in range(1, len(menu_options) + 1):
        print(f"{num}. {menu_options[num-1]}") 

def get_car_data():
    return clean_car_df(df.read_csv(CAR_FILE, sep="#"))

def get_review_data():
    return clean_review_df(df.read_csv(REVIEW_FILE, sep="\t"))

def clean_car_df(df):  
    return df

def clean_review_df(df):
    df["date"] = df["date"].apply(lambda x: dt.strptime(x, "%m-%d-%Y"))
    df["year"] = df["date"].apply(lambda x: x.year)
    df["month"] = df["date"].apply(lambda x: x.month)
    df["word_count"] = df["comment"].fillna("").apply(lambda x: len(re.sub("[^A-Za-z ]|(?<= ) ", "", str(x).strip()).strip().split(" ")))
    # Check is for null or empty comments that were not count
    df.loc[(df["comment"].isnull()) | (df["comment"].str.strip() == ""), "word_count"] = 0
    df.loc[df["rating"].isnull()]["rating"] = 0

    return df

def describe_col(df, col):
    print(f"\n{col.upper()} Statistics")
    print(df[col].describe(), end="\n\n")


def display_rating_by_year(df):
    rating_by_year = df.groupby(["year", "rating"])["rating"].value_counts().to_frame().reset_index()
    pivot_table = rating_by_year.pivot(values="count", columns="year", index="rating").fillna(0).astype(int)
    print(pivot_table)
    
    pivot_table.plot(kind="bar")
    plt.ylabel("Count")
    plt.yticks(np.arange(0,6,1))
    plt.xlabel("Rating")
    plt.title("Number of Ratings by Year")

    plt.show()

def display_average_word_count(df):
    word_count_by_year = df.groupby(["year"])["word_count"].mean().sort_values(ascending=False)
    word_count_by_year.name = "avg_word_count"
    word_count_by_year.plot(kind="bar")
    print(word_count_by_year)
    plt.yticks(np.arange(0, (word_count_by_year.max() + 1), .5))
    plt.ylabel("Word Count")
    plt.xlabel("Year")
    plt.xticks(rotation=0)
    plt.legend(loc="upper right")
    plt.show()

def display_ratings_count_distribution(df):
    df = df[(df["rating"].notnull()) & (df["comment"].notnull()) & (df["word_count"] > 0)]
    df["season"] = df.apply(lambda x: to_season(x["month"], x["year"]), axis=1)
    df["year_season"] = df.apply(lambda x: f"{x['year']}{to_season_ordinal(x['season'])}", axis=1)

    seasons_df = get_season_df(df["year"].min(), df["year"].max(), ["Winter", "Summer", "Fall"])
    
    df_by_season = df.groupby(["season"])["rating"].count().to_frame().reset_index()
    seasons_df["count"] = seasons_df["season"].apply(lambda x: df_by_season[df_by_season["season"] == x]["rating"].sum())
    seasons_df = seasons_df.set_index(["season"])
    print(seasons_df)

    seasons_df.plot(kind="line")
    plt.title("Number of Reviews by Season and Year")
    plt.ylabel("Count")
    plt.yticks(np.arange(0, (seasons_df["count"].max() + 2), 1))
    plt.xlabel("Year Season")
    plt.xticks(rotation=45)
    plt.show()

def to_season(month, year):
    season = ""
    if(month < 5):
        season = "Winter"
    elif(month < 9):
        season = "Summer"
    elif(month < 13):
        season = "Fall"
    return season + " " + str(year)
    
def to_season_ordinal(season):
    for [curr_seaason, ordinal] in [["Winter", 1], ["Summer", 2], ["Fall", 3]]:
        if(len(re.findall(curr_seaason, season, re.IGNORECASE)) > 0):
            return ordinal
    
def get_season_df(start_year, end_year, seasons = ["winter", "spring", "summer", "fall"]):
    all_seasons = []
    all_year_seasons = []
    for curr_year in range(start_year, end_year + 1):
        for curr_season_num in range(1, len(seasons) + 1):
            all_seasons.append(to_season(curr_season_num * 4, curr_year))
            all_year_seasons.append(f"{str(curr_year)}{str(to_season_ordinal(all_seasons[-1]))}")
    return df.DataFrame({"season": all_seasons, "year_season": all_year_seasons})

def display_yearly_ratings_by_car_make(review_df, car_df):
    review_df["make"] = review_df["name"].apply(lambda name: car_df[car_df["name"] == name]["make"].iloc[0])
    review_df.dropna(inplace=True)
    review_df = review_df.loc[(review_df["comment"].str.strip() != "")]
    
    year_make_group = review_df.groupby(["year", "make"])["rating"].mean().to_frame().reset_index()
    pivot_table = year_make_group.pivot(values="rating", index="year", columns="make")
    print(pivot_table)
    
    pivot_table.plot(kind="bar")
    plt.title("Average Yearly Rating by Car Make")
    plt.yticks(np.arange(0,5.5,.5))
    plt.ylabel("Average Rating")
    plt.xticks(rotation=0)
    plt.xlabel("Year")
    plt.show()

def display_avg_rating_by_car(df):
    df = df.loc[(df["rating"].notnull())]
    df = df.loc[df["comment"].str.strip() != ""]
    df = df.loc[df["comment"].notnull()]
    avg_rating = df.groupby(["name"])["rating"].mean().sort_values(ascending=True)
    print(avg_rating)

    avg_rating.plot(kind="bar")
    plt.xticks(rotation=0)
    plt.xlabel("Car Names")
    plt.ylabel("Average Rating")
    plt.show()

def display_avg_word_count_per_rating(df):
    df = df.loc[(df["rating"].notnull())]
    df = df.loc[df["comment"].str.strip() != ""]
    df = df.loc[df["comment"].notnull()]

    avg_rating_count = df.groupby(["rating"])["word_count"].mean()
    print(avg_rating_count)

    avg_rating_count.plot(kind="bar")
    plt.title("Average Word Count by Rating")
    plt.xlabel("Rating")
    plt.ylabel("Word Count")
    plt.show()



            
def pause():
    input("\nPress enter to continue...")
    print("\n")

main()
