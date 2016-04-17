# Main CCDB Program, implemented using Bokeh
import psycopg2
import numpy

from pandas import DataFrame
from pandas.io import sql

from bokeh.plotting import Figure
from bokeh.charts import Bar
from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, VBox, HBox, VBoxForm, Axis
from bokeh.models.widgets import TextInput, Select, Slider

### SQL Queries

STATES = """
    SELECT DISTINCT(state) FROM ccdb
        WHERE state IS NOT NULL
    """

PRODUCT_NAMES = """
    SELECT DISTINCT(product) FROM ccdb
        WHERE product IS NOT NULL
    """

ISSUE_NAMES = """
    SELECT DISTINCT(issue) FROM ccdb
        WHERE issue IS NOT NULL
    """

TOTAL_COMPLAINTS = """
    SELECT COUNT(*) FROM ccdb
    {}
    """

COMPLAINTS_WITH_MEDIAN_INCOME = """
    SELECT * FROM
    (SELECT zip_code, complaint_count, B06011_001 AS median_income FROM
        (SELECT zip_code, COUNT(*) AS complaint_count FROM ccdb
          {0}
          GROUP BY zip_code) AS ccdb_by_zip
        INNER JOIN g20135us
            ON ccdb_by_zip.zip_code=g20135us.zcta5
        INNER JOIN e20135us0015000
            ON g20135us.logrecno=e20135us0015000.logrecno AND
               B06011_001 IS NOT NULL
    ) AS ccdb_acs_by_zip
    {1}
    """

COMPLAINTS_BY_STATE = """
    SELECT * FROM
        (SELECT state, COUNT(*) AS complaint_count
            FROM ccdb
         {0}
         GROUP BY state) AS complaints
    {1}
    """

DISTINCT_MATCHED_ZIPCODES = """
    SELECT DISTINCT(zcta5) FROM ccdb
        INNER JOIN g20135us
            ON ccdb.zip_code=g20135us.zcta5;
    """

SUMMARY_DATA_BY_STATE = """
    SELECT * FROM
        (SELECT state, COUNT(*) AS complaint_count FROM ccdb
        INNER JOIN g20135us
            ON ccdb.zip_code=g20135us.zcta5
        INNER JOIN e20135us0015000
            ON g20135us.logrecno=e20135us0015000.logrecno
        {})
    {}
    GROUP BY ccdb.state
    """

### Step 1: Prepare initial data sources

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(
        "dbname='postgres' user='postgres' host='localhost'"
    )
except e:
    print "Error connecting to PostgreSQL: ", e

cur = conn.cursor()

# Get states
cur.execute(STATES)
states = sorted([x[0] for x in cur.fetchall()])
states.insert(0, "All")

# Get product names
cur.execute(PRODUCT_NAMES)
product_names = sorted([x[0] for x in cur.fetchall()])
product_names.insert(0, "All")

# Get issue names
cur.execute(ISSUE_NAMES)
issue_names = sorted([x[0] for x in cur.fetchall()])
issue_names.insert(0, "All")

# Create data source for state totals
state_source = ColumnDataSource(data=dict())
zip_source = ColumnDataSource(data=dict(x=[], y=[]))

### Step 2: Build the UI

# Build inputs
state_widget = Select(title="State", value="All", options=states)
issue_widget = Select(title="Issues", value="All", options=issue_names)
product_widget = Select(title="Products", value="All", options=product_names)
min_complaints_widget = Slider(title="Min # Complaints", value=0,
                               start=0, end=100, step=10)

# Helper Functions
def generate_where_clause(state=None, product=None,
                          issue=None, min_complaints=None):
    """
    Generate a where clause given a set of filters
    """
    where_inner = []
    where_outer = []

    if state and not state == "All":
        where_inner.append("ccdb.state = '{}'".format(state))

    if product and not product == "All":
        where_inner.append("ccdb.product = '{}'".format(product))

    if issue and not issue == "All":
        where_inner.append("ccdb.issue = '{}'".format(issue))

    if min_complaints:
        where_outer.append("complaint_count > {}".format(min_complaints))

    if len(where_inner) > 0:
        where_inner = "WHERE " + " AND ".join(where_inner)
    else:
        where_inner = ""

    if len(where_outer) > 0:
        where_outer = "WHERE " + " AND ".join(where_outer)
    else:
        where_outer = ""

    return where_inner, where_outer

def build_state_data(where_inner="", where_outer=""):
    """
    Generates a bar graph of complaint counts by state
    """
    query = COMPLAINTS_BY_STATE.format(where_inner, where_outer)
    cur.execute(query)
    cc_by_state = DataFrame(cur.fetchall(),
                            columns=['state', 'complaint_count'])
    cc_by_state.set_index('state', drop=False)

    return cc_by_state

def build_zip_data(where_inner="", where_outer=""):
    """
    Generates a scatter plot of complaint counts vs media income per zip code
    """
    query = COMPLAINTS_WITH_MEDIAN_INCOME.format(where_inner, where_outer)
    cur.execute(query)
    cc_by_zip = DataFrame(cur.fetchall(), columns = [
                          'zip_code', 'complaint_count', 'median_income'])
    cc_by_zip.set_index('zip_code')

    # There are over 20,000 zip codes, so let's just take a sample, if needed
    if len(cc_by_zip.index) > 5000:
        cc_by_zip = cc_by_zip.sample(5000)

    # Remove outliers to make for a easier to read plot
    cc_by_zip = cc_by_zip[
        numpy.abs(
            cc_by_zip.complaint_count - cc_by_zip.complaint_count.mean()
        ) <= (10*cc_by_zip.complaint_count.std())
    ]

    return cc_by_zip

def update(attrname, old, new):
    """
    Update the data sources using the generated where clause
    """
    where_inner, where_outer = generate_where_clause(
        state_widget.value, product_widget.value,
        issue_widget.value, min_complaints_widget.value
    )

    state_data = build_state_data(
        where_inner = where_inner,
        where_outer = where_outer
    )

    state_source.data = dict(
        x=state_data["state"],
        y=state_data["complaint_count"]
    )

    zip_data = build_zip_data(
        where_inner = where_inner,
        where_outer = where_outer
    )

    zip_source.data = dict(
        x=zip_data["median_income"],
        y=zip_data["complaint_count"]
    )

state_widget.on_change('value', update)
product_widget.on_change('value', update)
issue_widget.on_change('value', update)
min_complaints_widget.on_change('value', update)

### Step 3: Build the charts

# Build state bar chart
state_bar_chart = Bar(build_state_data(), label="state",
                      values='complaint_count', toolbar_location=None,
                      title="Complaints by State", width=1300, height=200,
                      ylabel="", xlabel="", color="#2cb34a")

# Build zip code scatter plot
zip_data = build_zip_data()
zip_source.data = dict(x = zip_data["median_income"],
                       y = zip_data["complaint_count"])
zip_scatter_plot = Figure(plot_height=500, plot_width=1000,
                          title="Complaints by Median Income",
                          title_text_font_size='14pt')
zip_scatter_plot.circle(x="x", y="y", source=zip_source, size=4,
                        color="#addc91", line_color=None, fill_alpha="0.95")
zip_xaxis = zip_scatter_plot.select(dict(type=Axis, layout="below"))[0]
zip_xaxis.formatter.use_scientific = False

### Step 4: Construct the document

# The Bar() function automatically adds the chart as a root object
# which is not desireable, so clear the "document" then re-add objects in the
# correct order.
curdoc().clear()

controls = HBox(
    VBoxForm(min_complaints_widget, state_widget, product_widget, issue_widget),
    width=250
)

income_chart = HBox(controls, zip_scatter_plot)

document = VBox(
    state_bar_chart,
    income_chart
)

curdoc().add_root(document)
