Data Dashboard

Install required packages:

pip install streamlit pandas numpy plotly openpyxl scikit-learn streamlit_lottie
# optional: pip install kaleido  (for static image export)


Save the app.py file in a folder.

(Optional) Put your CSV sales_data.csv in the same folder (or use the upload widget inside the app).

Run:

streamlit run app.py

Open the URL shown by Streamlit (usually http://localhost:8501) and use the sidebar to upload data or enable sample data.

Load Data

You upload a CSV (or the app uses sample data).

The app converts dates and prepares the dataset.

2️⃣ Apply Filters

You choose date range, products, and regions in the sidebar.

The dashboard shows only the filtered data.

3️⃣ Calculate KPIs

Total Sales

Total Orders

Total Quantity

Unique Products

These numbers are animated for a modern UI.

4️⃣ Build Animated Charts

Animated Time-Series Chart — shows sales over time with a play button.

Animated Bar Race — shows which product sells most every month.

Donut Charts — show product share & region share.

World Map Chart — shows sales by city using latitude/longitude.

5️⃣ Final Dashboard

Interactive charts (zoom, hover).

Animated widgets.

Modern UI with dark theme.

Table + download buttons for CSV/Excel.
