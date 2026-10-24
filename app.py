import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(page_title="Smart Bus System", page_icon="🚌", layout="wide")
st.title("🚌 SMART BUS Ticket Booking & Reservation System")

# --- SESSION STATE INIT (Data yaad rakhega) ---
if 'routes' not in st.session_state:
    st.session_state.routes = [
        {"route_id": "R101", "departure_city": "Karachi", "destination_city": "Hyderabad", "departure_time": "08:00 AM", "ticket_price": 1200, "total_seats": 40, "available_seats": 40},
        {"route_id": "R102", "departure_city": "Karachi", "destination_city": "Sukkur", "departure_time": "09:30 AM", "ticket_price": 2000, "total_seats": 36, "available_seats": 36},
        {"route_id": "R103", "departure_city": "Hyderabad", "destination_city": "Mirpur Khas", "departure_time": "11:00 AM", "ticket_price": 800, "total_seats": 32, "available_seats": 32},
        {"route_id": "R104", "departure_city": "Karachi", "destination_city": "Lahore", "departure_time": "07:00 PM", "ticket_price": 5000, "total_seats": 45, "available_seats": 45},
        {"route_id": "R105", "departure_city": "Sukkur", "destination_city": "Hyderabad", "departure_time": "02:00 PM", "ticket_price": 1500, "total_seats": 30, "available_seats": 30},
    ]
if 'bookings' not in st.session_state:
    st.session_state.bookings = []
if 'booking_ids' not in st.session_state:
    st.session_state.booking_ids = set()
if 'counter' not in st.session_state:
    st.session_state.counter = 1001

def find_route(route_id):
    for r in st.session_state.routes:
        if r["route_id"] == route_id:
            return r
    return None

# --- SIDEBAR MENU ---
menu = st.sidebar.radio("Menu", ["View Routes", "Search Route", "Book Ticket", "View Bookings", "Cancel Booking", "Seat Availability", "Booking Report"])

# 1. VIEW ROUTES
if menu == "View Routes":
    st.header("Available Bus Routes")
    st.table(st.session_state.routes)

# 2. SEARCH ROUTE
elif menu == "Search Route":
    st.header("Search Route")
    query = st.text_input("Enter Route ID or City (e.g. R101 or Karachi)")
    if query:
        results = [r for r in st.session_state.routes if query.lower() in r["route_id"].lower() or query.lower() in r["departure_city"].lower() or query.lower() in r["destination_city"].lower()]
        if results:
            st.success(f"{len(results)} routes found")
            st.table(results)
        else:
            st.error(f"No routes found for '{query}'")

# 3. BOOK TICKET
elif menu == "Book Ticket":
    st.header("Book a Ticket")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Passenger Name")
        age = st.number_input("Passenger Age", min_value=1, max_value=100, step=1)
    with col2:
        route_id = st.selectbox("Select Route", [r["route_id"] for r in st.session_state.routes])
        seats = st.number_input("Number of Seats", min_value=1, step=1)
    
    route = find_route(route_id)
    if route:
        st.info(f"Route: {route['departure_city']} -> {route['destination_city']} | Fare: Rs.{route['ticket_price']} | Available: {route['available_seats']}")

    if st.button("Confirm Booking"):
        if not name.strip():
            st.error("Name cannot be empty!")
        elif seats > route["available_seats"]:
            st.error(f"Only {route['available_seats']} seats available!")
        else:
            booking_id = f"B{st.session_state.counter}"
            st.session_state.counter += 1
            total_fare = route["ticket_price"] * seats
            new_booking = {
                "booking_id": booking_id, "passenger_name": name, "passenger_age": age,
                "route_id": route_id, "seats_booked": seats,
                "total_fare": total_fare, "status": "Confirmed"
            }
            st.session_state.bookings.append(new_booking)
            st.session_state.booking_ids.add(booking_id)
            route["available_seats"] -= seats
            st.success(f"Booking Confirmed! ID: {booking_id} | Total Fare: Rs.{total_fare}")

# 4. VIEW BOOKINGS
elif menu == "View Bookings":
    st.header("All Bookings")
    if st.session_state.bookings:
        st.table(st.session_state.bookings)
    else:
        st.warning("No bookings yet.")

# 5. CANCEL BOOKING
elif menu == "Cancel Booking":
    st.header("Cancel Booking")
    bid = st.text_input("Enter Booking ID (e.g. B1001)").upper()
    if st.button("Cancel"):
        found = False
        for b in st.session_state.bookings:
            if b["booking_id"] == bid:
                found = True
                if b["status"] == "Cancelled":
                    st.warning("Already cancelled! Seats restored only once.")
                else:
                    r = find_route(b["route_id"])
                    r["available_seats"] += b["seats_booked"]
                    b["status"] = "Cancelled"
                    st.success(f"{bid} cancelled. {b['seats_booked']} seats restored.")
                break
        if not found:
            st.error("Booking ID not found.")

# 6. SEAT AVAILABILITY
elif menu == "Seat Availability":
    st.header("Seat Availability")
    for r in st.session_state.routes:
        st.write(f"**{r['route_id']}** : {r['departure_city']} -> {r['destination_city']} | {r['available_seats']}/{r['total_seats']}")

# 7. BOOKING REPORT
elif menu == "Booking Report":
    st.header("Booking Report")
    confirmed = [b for b in st.session_state.bookings if b["status"] == "Confirmed"]
    cancelled = [b for b in st.session_state.bookings if b["status"] == "Cancelled"]
    col1, col2, col3 = st.columns(3)
    col1.metric("Confirmed Bookings", len(confirmed))
    col2.metric("Reserved Seats", sum(b["seats_booked"] for b in confirmed))
    col3.metric("Revenue", f"Rs. {sum(b['total_fare'] for b in confirmed)}")
    fully = [r["route_id"] for r in st.session_state.routes if r["available_seats"] == 0]
    st.write(f"**Fully Booked Routes:** {', '.join(fully) if fully else 'None'}")