import streamlit as st
import psycopg2
import pandas as pd
import datetime


def connection_to_db(dbname, user, password, host, port):
  try:
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    return conn
  except Exception as e:
    st.error(f"Connection error: {e}")
    return None


def run_query(conn, sql):
  if not conn:
    return

  cursor = conn.cursor()
  cursor.execute(sql)

  return cursor.fetchall(), cursor.description

def update_query(conn,sql):
    if not conn:
      return
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    return True

def show_available_listing(country, amenity,rating):
    country_filter = f"AND country.Country = '{country}'" if country else ""
    amenity_filter = f"AND amenity.Amenity_level = '{amenity}'" if amenity else ""
    rating_filter = f"AND rating.RatingLevel = '{rating}'" if rating else ""

    available_listing_sql = f"""
        SELECT
  listing.Listing_ID,
  listing.Name,
  listing.Description,
  listing.Location,
  property.propertytype,
  bedroom.bedtype,
  price.price,
  bathroom.bathroomtype,
  amenity.amenity_level,
  rating.RatingLevel,
  cancellation.CancellationType
FROM
  listing
INNER JOIN property ON listing.Property_ID = property.Property_ID
INNER JOIN bedroom ON listing.Bedroom_ID = bedroom.Bedroom_ID
INNER JOIN bathroom ON listing.Bathroom_ID = bathroom.Bathroom_ID
INNER JOIN amenity ON listing.Amenity_ID = amenity.amenity_ID
INNER JOIN price ON listing.Price_ID = price.price_id
INNER JOIN review ON listing.listing_id = review.listing_id
INNER JOIN rating ON review.rating_id = rating.rating_id
INNER JOIN cancellation ON listing.Cancellation_ID = cancellation.Cancellation_ID
INNER JOIN country ON listing.Country_ID = country.Country_ID
WHERE listing.Availability = 'Available'
    {country_filter}
    {amenity_filter}
    {rating_filter}

    """
   
    return available_listing_sql

def post_guest_review(guest_id,rating_level,total_rating,communication_rating,cleanliness_rating,location_rating,check_in_rating,current_date):
    post_review_sql = f"""
       UPDATE Review 
  SET 
    Host_ID = (SELECT host_id FROM listing WHERE guest_id = '{guest_id}'),
    Listing_ID = (SELECT listing_id FROM listing WHERE guest_id = '{guest_id}'),
    Rating_ID = (SELECT Rating_ID FROM Rating WHERE RatingLevel = '{rating_level}'),
    Review_Date = '{current_date}',
    Total_Rating = {total_rating},
    Communication_Rating = {communication_rating},
    Cleanliness_Rating = {cleanliness_rating},
    Location_Rating = {location_rating},
    CheckIn_Rating = {check_in_rating}
WHERE
    Guest_ID = '{guest_id}';

        """
    return post_review_sql

def check_booking_status(guest_id):
  booking_status_sql = f"""
                SELECT
                    Bookings.CheckInDate,
                    Bookings.CheckOutDate,
                    Listing.Name ,
                    Listing.Description,
                    Listing.Location,
                    Booking_Status.BookingStatus,
                    price.Price,
                    property.PropertyType,
                    room.RoomType,
                    amenity.Amenity_level,
                    bathroom.BathroomType
                FROM
                    Bookings 
                    JOIN Listing  ON Bookings.Listing_ID = Listing.Listing_ID
                    JOIN Booking_Status ON Bookings.Booking_Status_ID = booking_status.Booking_Status_ID
                    JOIN Price ON Listing.Price_ID = Price.Price_ID
                    JOIN Property ON Listing.Property_ID = property.Property_ID
                    JOIN Room ON Listing.Room_ID = room.Room_ID
                    JOIN Amenity ON Listing.Amenity_ID = amenity.Amenity_ID
                    JOIN Bathroom ON Listing.Bathroom_ID = bathroom.Bathroom_ID
                WHERE
                    Bookings.Guest_ID = {guest_id};
            """
  return booking_status_sql
dbname = "postgres"
user = "postgres"
password = "12345678"
host = "database-1.c9yya6oqef3n.us-east-2.rds.amazonaws.com"
port = 5432

conn = connection_to_db(dbname, user, password, host, port)

st.set_page_config(page_title="Team 67", page_icon="")

st.markdown(
        f"""
        <style>
            .stApp {{
                background-image: url('https://www.godsavethepoints.com/wp-content/uploads/2019/07/fairmont_tony_bennett_suite-3.jpeg');
                background-size: cover;
            }}

            .st-bc {{
                color: white;
                background-color: #0E1117;
            }}

            .stTextInput > div > div {{
                background-color: #f0f2f6;
                border-color: #8aa2a9;
            }}
            
            
            .st-bb {{
                font-size: 20px;
                color: yellow; 
                font-weight: bold; 
            }}
        </style>
        """,
        unsafe_allow_html=True
    )

st.header("Hotel System")
st.image("https://olirdesigns.com/wp-content/uploads/2021/06/hotel-dora-logo.png", width=100)
search_hotels, review_hotels,book_status_hotels = st.tabs(["Seach Hotels", "Review Hotels", "Book Hotels"])

with search_hotels:

  st.subheader("Find your hotel")

  country = st.selectbox("Country", ["USA", "Canada", "UK", "Australia", "Germany","France", "Italy", "Spain", "China", "India"], key=1)
  amenity = st.selectbox("Amentity", ['Basic', 'Standard', 'Comfort', 'Premium', 'Luxury'], key=2)
  rating = st.selectbox("Rating ", ["Excellent", "Very Good", "Good", "Fair", "Poor"], key=3)

  if st.button("Show", key=4):
    available_listing = show_available_listing(country, amenity,rating)
    results, description = run_query(conn, available_listing)
    results_df = pd.DataFrame(results, columns=[desc[0] for desc in description])

    st.dataframe(results_df)

  
with review_hotels:
  st.subheader("Post review:")
  guest_id = st.text_input("Your Guest ID",key=21)
  rating_level = st.selectbox("Your Overall Rating Level", ["Poor", "Fair", "Good", "Very Good", "Excellent"],key=12)
  total_rating = st.slider("Your Overall Rating", 1, 5, 3,key=13)
  communication_rating = st.slider("Communication Rating", 1, 5, 3,key=14)
  cleanliness_rating = st.slider("Cleanliness Rating", 1, 5, 3,key=15)
  location_rating = st.slider("Location Rating", 1, 5, 3,key=16)
  check_in_rating = st.slider("Check-In Rating", 1, 5, 3,key=17)
  current_date = datetime.date.today().strftime("%Y-%m-%d")
    
  if st.button("Submit Review",key=18):
    post_review = post_guest_review(guest_id,rating_level,total_rating,communication_rating,cleanliness_rating,location_rating,check_in_rating,current_date) 
    update_query(conn, post_review)
    st.success("Thank you for your review!")

with book_status_hotels:
  st.subheader("Check your booking Status")
  guest_id = st.text_input("Your Guest ID to check your booking",key=31)
  if st.button("Check",key=32):
    check_status = check_booking_status(guest_id)
    booking_details,_= run_query(conn, check_status)

    if booking_details:
      for detail in booking_details:
        check_in_date, check_out_date, listing_name, description, location,booking_status, price, property_type, room_type, amenity_level, bathroom_type = detail
                              
        st.write(f"**Listing Name:** {listing_name}")
        st.write(f"**Check-In Date:** {check_in_date}")
        st.write(f"**Check-Out Date:** {check_out_date}")
        st.write(f"**Location:** {location}")
        st.write(f"**Price:** {price}")
        st.write(f"**Property Type:** {property_type}")
        st.write(f"**Room Type:** {room_type}")
        st.write(f"**Amenity Level:** {amenity_level}")
        st.write(f"**Bathroom Type:** {bathroom_type}")
        st.write(f"**Booking Status:** {booking_status}")
        st.write(f"**Description:** {description}")