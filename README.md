# Book Search & Queries Application
# Overview
- This application is a comprehensive tool for fetching, storing, and analyzing book data using the Google Books API.
- Built with Python, PostgreSQL, and Streamlit, it enables users to search for books, store data in a PostgreSQL database, and perform SQL queries to extract insights.
- Leveraging Python libraries like Streamlit for interactive visualization, the application provides a seamless interface for exploring and analyzing book data fetched from the API.

---

## Features

### 1. **Fetch and Save Book Data**
- Fetch book data from the Google Books API based on a query.
- Save the fetched data into a CSV file for further processing.

### 2. **Data Cleaning and Transformation**
- Remove duplicates and handle missing data.
- Convert columns to appropriate data types for consistency and error prevention.

### 3. **Database Integration**
- Store the cleaned book data in a PostgreSQL database.
- Use SQL to query data directly from the database.

### 4. **Interactive Dashboard**
- Search books interactively based on keywords (title, author, or publisher).
- Run pre-defined SQL queries to analyze data.
- Visualize query results using Seaborn and Matplotlib.

---

## Installation

### Prerequisites
- Python 3.8 or later
- PostgreSQL database
- Environment variables for API key and database connection details

### Libraries
Install the required Python libraries using pip:

```bash
pip install pandas streamlit matplotlib seaborn psycopg2 python-dotenv requests sqlalchemy
