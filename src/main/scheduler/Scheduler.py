from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
#first make sure the right number of things were in the input, i.e. create_patient <username> <password?
    if len(tokens) != 3:
        print("Failed to create user.")
        start()
        return

    #parse the input; python index starts at 0, not 1
    username = tokens[1]
    password = tokens[2]

#check if username is taken
    if username_exists_patient(username): #defined below
        print("Username taken, try again!")
        start()
        return

#if we pass the above checks, we can finally make the patient
    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

        # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        start()
        return
    print("Created user ", username)
    start()

    

def username_exists_patient(username): #taken from caregivers example below
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patient WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        start()
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        start()
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        start()
        return
    print("Created user ", username)
    start()


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    #based off of the login_caregiver example below
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        start()
        return
    
    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        start()
        return
    
    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        start()
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient
        start()

        

def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        start()
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        start()
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        start()
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver
        start()


def search_caregiver_schedule(tokens):
    if len(tokens) ==0:
        print("Please try again!")
        start()
        return

    #if "-" not in tokens
        #print("Please try again!")
        #start()
        #return     
    
    date = tokens[1]
    date_split = date.split("-")

    #check if the date format is correct mm-dd-yyyy
    if len(date_split) != 3:
        print("Please try again!")
        start()
        return
    
    if len(date_split[0]) != 2:
        print("Please try again!")
        start()
        return

    if len(date_split[1]) != 2:
        print("Please try again!")
        start()
        return

    if len(date_split[2]) != 4:
        print("Please try again!")
        start()
        return 
    
    month = int(date_split[0])
    day = int(date_split[1])
    year = int(date_split[2])

    if month==00 or day==00 or year==0000:
        print("Please try again!")
        start()
        return

    if month >12 or day>31:
        print("Please try again!")
        start()
        return   

    #check if a user is logged in (can be either patient or caregiver)
    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        start()
        return

    #find available caregivers
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    my_str=""
    
    find_caregiver_for_date = "SELECT Username FROM Availabilities WHERE Time = %s ORDER BY Username ASC"
    try:
        d = datetime.datetime(year, month, day)#dates are stored this way in sql
        cursor.execute(find_caregiver_for_date, d)
        c_results = cursor.fetchall()
        if len(c_results)!= 0:
            for row in c_results:  
                my_str += row['Username']+" "
            print(my_str)
        else:
            print('Please try again! There are no caregivers available on that date.')
        cm.close_connection()
    except pymssql.Error:
        print("Please try again!")
        cm.close_connection()

    #find available vaccines
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)
    
    find_vaccine_stock= "SELECT * FROM Vaccines"
    try:
        cursor.execute(find_vaccine_stock)
        v_results = cursor.fetchall()
        if len(v_results)!= 0:
            for row in v_results:
                print(row['Name'], row['Doses'])
        else:
            print('No vaccines available.')
        cm.close_connection()
    except pymssql.Error:
        print("Please try again!")
        cm.close_connection()
    start()


def reserve(tokens):
    global current_patient
    global current_caregiver

    #make sure that not caregiver logged in
    if current_caregiver is not None:
        print("Please login as a patient!")
        start()
        return

    #make sure a patient is logged in
    if current_patient is None:
        print("Please login first!")
        start()
        return

    #make sure the input is the right amount of stuff (reserve,date,vaccine)
    if len(tokens) != 3:
        print("Please try again!")
        start()
        return

    date =tokens[1]
    vaccine =tokens[2]
    date_split = date.split("-")

    #check if the date format is correct mm-dd-yyyy
    if len(date_split) != 3:
        print("Please try again!")
        start()
    
    if len(date_split[0]) != 2:
        print("Please try again!")
        start()
        return

    if len(date_split[1]) != 2:
        print("Please try again!")
        start()
        return

    if len(date_split[2]) != 4:
        print("Please try again!")
        start()
        return 
    
    month = int(date_split[0])
    day = int(date_split[1])
    year = int(date_split[2])

    if month==00 or day==00 or year==0000:
        print("Please try again!")
        start()
        return

    if month >12 or day>31:
        print("Please try again!")
        start()
        return   

    #find available caregivers on that date
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)
    
    #order caregiver list alphabetically
    find_caregiver_for_date = "SELECT Username FROM Availabilities WHERE Time =  %s ORDER BY Username ASC"
    try:
        d = datetime.datetime(year, month, day)
        cursor.execute(find_caregiver_for_date,d)
        cg_results=cursor.fetchall()
        if len(cg_results) != 0:
            caregiver_list = [row['Username'] for row in cg_results]
            #want to pick the first on the list alphabetically:
            book_caregiver = caregiver_list[0]
        else:
            print('No Caregiver is available!')
            cm.close_connection()
            start()
            return
    except pymssql.Error:
        print("Please try again!")
        cm.close_connection()
        start()
        return
    cm.close_connection()



    #check that the requested vaccine is available
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    find_vaccine= "SELECT Name, Doses FROM Vaccines WHERE Name= %s"
    
    try:
        cursor.execute(find_vaccine, vaccine)
        vaxlist = cursor.fetchall()
        if len(vaxlist) == 0:
            print('Not enough available doses!')  #no vaccines with that name available
            cm.close_connection()
            start()
            return
        for row in vaxlist: #now if we have that vaccine name in our database...
            avail_doses = row[1] #this entry is the dose number
            if avail_doses > 0:#if we have some!

                
                
                # Update the vaccine's dose count
                avail_doses -= 1
                update_vaccine_doses = "UPDATE Vaccines SET Doses = " +str(avail_doses) +" WHERE name = \'" + vaccine + "\'"
                #del_vaccine = "DELETE FROM Vaccines WHERE Name= %s"
                #insert_vaccine="INSERT INTO Vaccines VALUES (%s, %s)"
                

                try:
                    #cursor.execute(del_vaccine, vaccine)
                    #conn.commit()
                    
                    #cursor.execute(insert_vaccine, (vaccine, str(avail_doses-1)))
                    cursor.execute(update_vaccine_doses)
                    conn.commit()
             
                except pymssql.Error:
                    print("Please try again!")
                    cm.close_connection()
                    start()
                    return
                cm.close_connection()
            else:  # avail_dose = 0
                print("Not enough available doses!")  # vaccine name in our list but no doses ready
                cm.close_connection()
                start()
                return
    except pymssql.Error:
        print("Please try again!")
        cm.close_connection()
        start()
        return
    cm.close_connection()

    

    #remove availablity of that caregiver on that date
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    
    del_avail = "DELETE FROM Availabilities WHERE Time= %s AND Username= %s"
    try:
        cursor.execute(del_avail,(d,book_caregiver))
        conn.commit()
    except pymssql.Error:
        print("Please try again!")
        cm.close_connection()
        start()
        return
    cm.close_connection()


    

    #lastly, add the appointment to the database
    
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    
    find_max_id = "SELECT MAX(ID) from Appointments"
    #we need to assign the appt an ID number, I'll just make it bigger than the existing ones

    try:
        cursor.execute(find_max_id)
        
        maxresults=cursor.fetchall()
        if maxresults[0][0] is None:
            appointment_id = 1 #this is the first appointment ever!
        else:
            appointment_id = int(maxresults[0][0])+1 #the appt ID is one bigger than the current biggest
    except pymssql.Error:
        print("Please try again!")
        cm.close_connection()
        start()
        return

    #add new appt
    add_appointment = "INSERT INTO Appointments values(%d,%s,%s,%s,%s)"  
    try:
        cursor.execute(add_appointment,(appointment_id, d, current_patient.username, book_caregiver, vaccine))
        print("Appointment ID: " + str(appointment_id)+ " Caregiver username: " +str(book_caregiver))
        conn.commit()
    except pymssql.Error:
        print("Please try again!")
        cm.close_connection()
    cm.close_connection()
    start()


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        start()
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        start()
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        start()
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        start()
        return
    print("Availability uploaded!")
    start()


def cancel(tokens):
    global current_caregiver
    global current_patient

    if len(tokens) != 2:
        print("Please try again!")
        start()
        return

    if current_caregiver== None and current_patient== None:
        print("Please log in first!")
        start()
        return

    inputID=tokens[1]

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    find_appt = "SELECT * FROM Appointments WHERE ID= %s"
    try:
        cursor.execute(find_appt, inputID)
        appts=cursor.fetchall()
        if len(appts) !=0: #this appt number exists
            for row in appts: #there is hopefully just one row here
                book_date= row[1]
                book_caregiver= row[3]
                book_vaccine= row[4]
                book_patient= row[2]

                #if current_caregiver != book_caregiver and current_patient != book_patient:
                   # print("Please try again! (can't cancel appt that is not yours)")
                   # return

                #delete appointment
                delete_appt = "DELETE FROM Appointments WHERE ID=%s"
                try:
                    cursor.execute(delete_appt, inputID)
                    conn.commit()
                except pymssql.Error:
                    print("Please try again!")
                    cm.close_connection()
                    start()
                    return
                cm.close_connection()

                #add a vaccine back to the vaccine table!
                cm = ConnectionManager()
                conn = cm.create_connection()
                cursor = conn.cursor()
                add_vax = "UPDATE Vaccines SET Doses = Doses+1 WHERE name=%s"
                try:
                    cursor.execute(add_vax, book_vaccine)
                    conn.commit()
                except pymssql.Error:
                    print("Please try again!")
                    cm.close_connection()
                    start()
                    return
                cm.close_connection()

                #add availability for caregiver back to the table!
                cm = ConnectionManager()
                conn = cm.create_connection()
                cursor = conn.cursor()
                add_availability = "INSERT INTO Availabilities VALUES (%s, %s)"
                try:
                    cursor.execute(add_availability, (str(book_date), str(book_caregiver)))
                    conn.commit()
                    print("Appointment successfully cancelled.")
                except pymssql.Error:
                    print("Please try again!")
                    cm.close_connection()
                    start()
                    return
                cm.close_connection()
                
        else: #there is not an appt with that number
            print("Please try again! (appt no. does not exist)")
            cm.close_connection()
            start()
            return
    except pymssql.Error:
        print("Please try again!")
        cm.close_connection()
        start()
        return
    start()   


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        start()
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        start()
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        start()
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            start()
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            start()
            return
    print("Doses updated!")
    start()


def show_appointments(tokens):
    global current_caregiver
    global current_patient

    #someone gotta be logged in
    if current_patient== None and current_caregiver == None:
        print("Please log in first!")
        start()
        return
    

    if current_patient != None: #get patient appointments
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)
        

    #in my Appointment table: ID, Time, Patient_name, Caregiver_name, Vaccine_name        
    
        p_appt = "SELECT * FROM Appointments WHERE Patient_name=%s ORDER BY ID ASC"
        try:
            cursor.execute(p_appt,current_patient.username)
            p_results = cursor.fetchall()
            
            if len(p_results) == 0:  #patient has no appointments
                print('Please try again! (No appointments)')
                cm.close_connection()
                start()
                return
            else:
                for row in p_results:
                    print(row['ID'], row['Vaccine_name'], row['Time'], row['Caregiver_name'])
        except pymssql.Error:
            print("Please try again!")
            cm.close_connection()
            start()
            return
        cm.close_connection()



    if current_caregiver != None: #get caregiver appointments
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

    #in my Appointment table: ID, Time, Patient_name, Caregiver_name, Vaccine_name        
    
        c_appt = "SELECT * FROM Appointments WHERE Caregiver_name=%s ORDER BY ID ASC"
        try:
            cursor.execute(c_appt,current_caregiver.username)
            results = cursor.fetchall()
            
            if len(results) == 0:  #caregiver has no appointments
                print('Please try again! (No appointments)')
                cm.close_connection()
                start()
                return
            else:
                for row in results:
                    print(row['ID'], row['Vaccine_name'], row['Time'], row['Patient_name'])
        except pymssql.Error:
            print("Please try again!")
            cm.close_connection()
            start()
            return
        cm.close_connection()
    start()


def logout(tokens):
    global current_caregiver
    global current_patient

    try:
        if current_patient is None and current_caregiver is None:
            print("Please login first!")
            start()
            return
        else:
            current_caregiver=None
            current_patient=None
            print("Successfully logged out!")
            start()
            return
    except pymssql.Error:
        print("Please try again!")
        start()
        return
    start()


def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")
            start()


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
