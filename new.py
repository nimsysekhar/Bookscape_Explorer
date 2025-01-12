import pandas as pd
import streamlit as st
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns

# Load environment variables


# Set page configuration
st.set_page_config(
    layout="wide",
    page_title="Book Search & Queries",
    page_icon="📚"
)

# Add custom background color
st.markdown(
    """
    <style>
    body {
        background-color: #fdf5e6; /* Nude theme color */
        color: #5a3e36; /* Brown text color */
    }
    .stButton>button {
        background-color: #5a3e36; /* Brown button background */
        color: white; /* Button text color */
        border: none;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #8b5e3c; /* Lighter brown for hover effect */
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def load_data():
    # Establish database connection
    connection = psycopg2.connect(
            database='bookscape_explorer', 
            port = 5432, 
            user='postgres',
            host='localhost',
            password='1234',
    )
    # Query the database
    df = pd.read_sql_query("SELECT * FROM books;", connection)
    connection.close()  # Close connection after fetching data
    return df

# Load the data at the start
df = load_data()

# Define the search function
def search_books(keyword, df):
    keyword = keyword.lower()
    result = df[
        df['book_title'].str.lower().str.contains(keyword, na=False) |
        df['book_authors'].str.lower().str.contains(keyword, na=False) |
        df['publisher'].str.lower().str.contains(keyword, na=False)
    ]
    return result

# Layout: Left (queries) and Right (search optimization)
left_col, right_col = st.columns([1, 2])  # Adjusted proportions for size

# Right Column: Search box
with right_col:
    st.title("📚 Book Search")

    # Input keyword
    keyword = st.text_input("Enter a keyword to search:", key="search")

    # Search button
    if st.button("Search"):
        search_results = search_books(keyword, df)
    
        if not search_results.empty:
            st.write(f"Found {len(search_results)} matching books:")
            for _, row in search_results.iterrows():
                try:
                    # Use the image link if available, otherwise use the fallback URL
                    image_url = (
                        row['imageLinks'] 
                        if pd.notnull(row['imageLinks']) and row['imageLinks'].strip() 
                        else "https://st4.depositphotos.com/14953852/24787/v/450/depositphotos_247872612-stock-illustration-no-image-available-icon-vector.jpg"
                    )
                    # Display the image and the book details
                    st.image(image_url, caption=row['book_title'], width=150)
                    st.write(f"Author: {row['book_authors']}")
                except Exception as e:
                    st.warning(f"Error loading image: {e}")
                    st.write(row['book_title'])  # Show title in case of image loading failure
        else:
            st.warning("No books found matching your search.")

# Left Column: Run Queries
with left_col:
    st.subheader("Run SQL Queries")

    # List of SQL queries
    queries = [
        "Check Availability of eBooks vs Physical Books",
        "Find the Publisher with the Most Books Published",
        "Identify the Publisher with the Highest Average Rating",
        "Get the Top 5 Most Expensive Books by Retail Price",
        "Find Books Published After 2010 with at Least 500 Pages",
        "List Books with Discounts Greater than 20%",
        "Find the Average Page Count for eBooks vs Physical Books",
        "Find the Top 3 Authors with the Most Books",
        "List Publishers with More than 10 Books",
        "Find the Average Page Count for Each Category",
        "Retrieve Books with More than 3 Authors",
        "Books with Ratings Count Greater Than the Average",
        "Books with the Same Author Published in the Same Year",
        "Books with a Specific Keyword in the Title",
        "Year with the Highest Average Book Price",
        "Count Authors Who Published 3 Consecutive Years",
        "Write a SQL query to find authors who have published books in the same year but under different publishers. Return the authors, year, and the COUNT of books they published in that year.",
        "Create a query to find the average amount_retailPrice of eBooks and physical books. Return a single result set with columns for avg_ebook_price and avg_physical_price. Ensure to handle cases where either category may have no entries.",
        "Write a SQL query to identify books that have an averageRating that is more than two standard deviations away from the average rating of all books. Return the title, averageRating, and ratingsCount for these outliers.",
        "Create a SQL query that determines which publisher has the highest average rating among its books, but only for publishers that have published more than 10 books. Return the publisher, average_rating, and the number of books published."
    ]

        # Corresponding SQL queries for each option
    query_sql = [
        '''
        SELECT
        COUNT(CASE WHEN "isEbook" = TRUE THEN 1 END) AS ebook_availability,
        COUNT(CASE WHEN "isEbook" = FALSE THEN 1 END) AS physical_book_availability 
        FROM books;
        ''',
        '''
        SELECT publisher, COUNT(*) AS books_published
        FROM books
        WHERE publisher IS NOT NULL AND publisher != 'nan'
        GROUP BY publisher
        ORDER BY books_published DESC
        LIMIT 1;
        ''',
        '''
        SELECT publisher, MAX("averageRating") AS avg_rating
        FROM books
        GROUP BY publisher
        ORDER BY avg_rating ASC
        LIMIT 1;
        ''',
        '''
        SELECT book_title, "amount_retailPrice"
        FROM books
        ORDER BY "amount_retailPrice" DESC
        LIMIT 5;
        ''',
        '''
        SELECT book_title, year, "pageCount"
        FROM books
        WHERE year > '2010' AND "pageCount" >= 500;
        ''',
        '''
        SELECT 
            book_title, 
            "amount_listPrice", 
            "amount_retailPrice", 
            ("amount_listPrice" - "amount_retailPrice") / "amount_listPrice" * 100 AS discount_percentage 
        FROM books 
        WHERE "amount_listPrice" > 0 
        AND ("amount_listPrice" - "amount_retailPrice") / "amount_listPrice" > 0.2;
        ''',
        '''
        SELECT 
            "isEbook", 
            AVG("pageCount") AS avg_page_count 
        FROM books 
        GROUP BY "isEbook";
        ''',
        '''
        SELECT 
            UNNEST(STRING_TO_ARRAY(book_authors, ',')) AS author, 
            COUNT(*) AS book_count 
        FROM books 
        GROUP BY author 
        ORDER BY book_count DESC 
        LIMIT 4;
        ''',
        '''
        SELECT 
            publisher, 
            COUNT(*) AS book_count 
        FROM books 
        GROUP BY publisher 
        HAVING COUNT(*) > 10;
        ''',
        '''
        SELECT 
            categories, 
            AVG("pageCount") AS avg_page_count
        FROM books 
        GROUP BY categories;
        ''',
        '''
        SELECT 
            book_title, 
            book_authors 
        FROM books 
        WHERE ARRAY_LENGTH(STRING_TO_ARRAY(book_authors, ','), 1) > 3;
        ''',
        '''
        SELECT 
            book_title, 
            "ratingsCount" 
        FROM books 
        WHERE "ratingsCount" > (SELECT AVG("ratingsCount") FROM books);
        ''',
        '''
        SELECT 
            book_authors, 
            year, 
            COUNT(*) AS book_count 
        FROM books 
        GROUP BY book_authors, year 
        HAVING COUNT(*) > 1;
        ''',
        '''
        SELECT 
            book_title 
        FROM books 
        WHERE book_title ILIKE '%<specific_keyword>%';
        ''',
        '''
        SELECT 
            year, 
            AVG("amount_retailPrice") AS avg_price 
        FROM books 
        GROUP BY year 
        ORDER BY avg_price ASC 
        LIMIT all;
        ''',
        '''
        WITH consecutive_years AS (
            SELECT
                book_authors,
                ROUND(CAST(year AS NUMERIC)) AS year_int, -- Cast to NUMERIC then ROUND
                LEAD(ROUND(CAST(year AS NUMERIC)), 1) OVER (PARTITION BY book_authors ORDER BY ROUND(CAST(year AS NUMERIC))) AS next_year,
                LEAD(ROUND(CAST(year AS NUMERIC)), 2) OVER (PARTITION BY book_authors ORDER BY ROUND(CAST(year AS NUMERIC))) AS third_year
            FROM books
        )
        SELECT
            book_authors
        FROM consecutive_years
        WHERE next_year = year_int + 1
        AND third_year = year_int + 2
        GROUP BY book_authors;
        ''',
        '''
        SELECT 
            book_authors, 
            year, 
            COUNT(DISTINCT publisher) AS publisher_count 
        FROM books 
        GROUP BY book_authors, year 
        HAVING COUNT(DISTINCT publisher) > 1;
        ''',
        '''
        SELECT 
            AVG(CASE WHEN "isEbook" THEN "amount_retailPrice" END) AS avg_ebook_price, 
            AVG(CASE WHEN NOT "isEbook" THEN "amount_retailPrice" END) AS avg_physical_price 
        FROM books;
        ''',
        '''
        WITH stats AS (
            SELECT 
                AVG("averageRating") AS avg_rating, 
                STDDEV("averageRating") AS stddev_rating 
            FROM books
        )
        SELECT 
            book_title, 
            "averageRating", 
            "ratingsCount" 
        FROM books, stats 
        WHERE "averageRating" > avg_rating + 2 * stddev_rating 
        OR "averageRating" < avg_rating - 2 * stddev_rating;
        ''',
        '''
        SELECT 
            publisher, 
            AVG("averageRating") AS avg_rating, 
            COUNT(*) AS book_count 
        FROM books 
        GROUP BY publisher 
        HAVING COUNT(*) > 10 
        ORDER BY avg_rating DESC 
        LIMIT 1;
        '''
    ]

    # Select a query from the dropdown
    selected_query = st.selectbox("Select a Query", queries)

    # Find the SQL for the selected query
    selected_sql = query_sql[queries.index(selected_query)]

    # Execute the query and display results
    if st.button("Run Query", key="query_button"):
        try:
            # Connect to the PostgreSQL database
            connection = psycopg2.connect(
            database='bookscape_explorer', 
            port = 5432, 
            user='postgres',
            host='localhost',
            password='1234',
            )
            cursor = connection.cursor()

            # Execute the query
            cursor.execute(selected_sql)
            columns = [desc[0] for desc in cursor.description]  # Get column names
            data = cursor.fetchall()  # Fetch data

            # Display the query output
            df_query = pd.DataFrame(data, columns=columns)
            st.write("Query Results:")
            st.dataframe(df_query)

           # Visualization with Seaborn
            st.subheader("Visualization")
            fig, ax = plt.subplots(figsize=(10, 6))

            if df_query.shape[1] == 1:
                # Single column: bar chart
                sns.barplot(x=df_query.index, y=df_query.iloc[:, 0], ax=ax)
                ax.set_title("Bar Chart of Query Results")
                ax.set_ylabel(df_query.columns[0])
            elif df_query.shape[1] == 2:
                # Two columns: bar chart
                sns.barplot(x=df_query.iloc[:, 0], y=df_query.iloc[:, 1], ax=ax)
                ax.set_title("Bar Chart of Query Results")
                ax.set_xlabel(df_query.columns[0])
                ax.set_ylabel(df_query.columns[1])
            else:
                # More than two columns: aggregate to show a bar chart
                # Assuming the first column can be a categorical x-axis, and the rest can be stacked as bars
                df_melted = df_query.melt(id_vars=df_query.columns[0], var_name="Category", value_name="Value")
                
                sns.barplot(x=df_melted[df_query.columns[0]], y=df_melted["Value"], hue=df_melted["Category"], ax=ax)
                ax.set_title("Bar Chart of Query Results with Multiple Categories")
                ax.set_xlabel(df_query.columns[0])
                ax.set_ylabel("Value")

            # Rotate x-axis labels 90 degrees for better readability
            plt.xticks(rotation=90)

            st.pyplot(fig)
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()