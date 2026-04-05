import matplotlib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

#SETUP

FILE_PATH = r'C:\Users\admin\Downloads\No_hopes_L.xlsx' 
TIME_COL = 'time'
ALT_COL = 'altitude'
PRES_COL = 'pressure' 
# This variable defines the size of our moving average filter.
FILTER_WINDOW = 50

# LOAD DATA

# This line tells pandas to read the Excel file specified in FILE_PATH.
# It loads all the data into a "DataFrame" (like a smart spreadsheet) 
rawfile = pd.read_excel(FILE_PATH)


# APPLY FILTER

# This creates a new column in our DataFrame called 'filt_alt'.
rawfile['filt_alt'] = rawfile[ALT_COL].rolling(window=FILTER_WINDOW, center=False).mean()

# This creates a new column in our DataFrame called 'filt_pres'.
rawfile['filt_pres'] = rawfile[PRES_COL].rolling(window=FILTER_WINDOW, center=False).mean()

# This line cleans up the data and creates our final simulation DataFrame:
simulation = rawfile.dropna().reset_index(drop=True)

# INITIALIZE VARIABLES

# This is a "boolean flag" . We'll set it to True when we find apogee.
apogee_detected = False
# This variable will store the final apogee altitude. We start it at 0.
apogee_alt = 0.0
# This variable will store the final apogee time. We start it at 0.
apogee_time = 0.0

# This is another switch to see if the rocket has launched.
launch_detected = False
# This constant defines the altitude (100 meters) the rocket must pass.
LAUNCH_ALTITUDE_THRESHOLD = 100 

# Logic Variables for PRESSURE 

# This variable will always track the lowest pressure seen so far.
# We initialize it to positive infinity so the first real pressure is guaranteed to be lower.
min_pressure_so_far = np.inf             
# This variable will store the *time* at which the 'min_pressure_so_far' was recorded.
apogee_time_at_min_pressure = 0.0             
# This variable will store the *altitude* at which the 'min_pressure_so_far' was recorded.
apogee_alt_at_min_pressure = 0.0
# This is a counter that tracks how many *consecutive* rising pressure readings we've seen.
consecutive_pressure_increases = 0               
# This constant is the number of consecutive readings we need to *confirm* descent.
PRESSURE_INCREASE_COUNT = 3       



# MAIN LOOP 

# We start from '0' 
for i in range(0, len(simulation)):
    
    # '.iloc[i]' gets the entire row of data at the current index 'i'.
    row_curr = simulation.iloc[i]

    # Get the 'time' value from the current row.
    t = row_curr[TIME_COL]
    # Get the filtered 'altitude' value from the current row.
    alt = row_curr['filt_alt']
    #  Get the filtered 'pressure' value 
    pres = row_curr['filt_pres']
    
    # Launch Check
    # This 'if' block only runs if we haven't detected launch yet.
    if not launch_detected:
        # Check if the current altitude is higher than our launch threshold.
        if alt > LAUNCH_ALTITUDE_THRESHOLD:
            # If it is, set the launch "switch" to True. This block will never run again.
            launch_detected = True
            

    #  Apogee Logic 
    # This 'elif' (else if) block only runs if:
    #   1. 'launch_detected' IS True
    #   AND
    #   2. 'apogee_detected' is NOT True (we're still looking for it)
    elif not apogee_detected: 
        
       
        # Apogee Logic (Pressure-Based) 
        
        # A) This 'if' statement checks if the current pressure is a new record low.
        if pres < min_pressure_so_far:
            # If it is, update 'min_pressure_so_far' to this new, lower pressure.
            min_pressure_so_far = pres
            # We also record the *time and altitude* this new record was set.
            # This is our new *best guess* for the apogee point.
            apogee_time_at_min_pressure = t
            apogee_alt_at_min_pressure = alt
            
            # If pressure is dropping, we are NOT descending. Reset the counter.
            consecutive_pressure_increases = 0
            
        # B) This 'else' block runs if the pressure is rising (or the same).
        else:
            # We *might* be descending. Increment our "consecutive rising" counter.
            consecutive_pressure_increases += 1
            
        # C) This 'if' statement checks if our counter has reached the confirmation limit.
        if consecutive_pressure_increases >= PRESSURE_INCREASE_COUNT:
            
            # If it has, we are *sure* the rocket is descending.
            # Set the apogee "switch" to True. This whole 'elif' block will stop running.
            apogee_detected = True
            
            # Lock in the final apogee values.
            # We use the values we saved when pressure was at its *true minimum*.
            apogee_alt = apogee_alt_at_min_pressure
            apogee_time = apogee_time_at_min_pressure
            
            break 


#PLOT THE GRAPH


# This command creates a new "Figure" (the window) and "Axes" (the plotting area).
fig, ax1 = plt.subplots(figsize=(12, 8))

# Define a color for our altitude line.
color = 'tab:blue'
# Set the text for the X-axis (bottom).
ax1.set_xlabel('Time (seconds)', fontsize=12)
# Set the text for the Y-axis (left).
ax1.set_ylabel('Filtered Altitude (m)', color=color, fontsize=12)
# This is the main plot command. It plots 'time' on the x-axis and 'filt_alt' on the y-axis.
ax1.plot(simulation[TIME_COL], simulation['filt_alt'], color=color, label="Filtered Altitude")
# This tells the plot to make the Y-axis number labels the same color as our line.
ax1.tick_params(axis='y', labelcolor=color)
# This adds a dotted grid to the plot.
ax1.grid(True, linestyle=':')

# This draws a horizontal (axhline) line at the 'LAUNCH_ALTITUDE_THRESHOLD' value.
ax1.axhline(y=LAUNCH_ALTITUDE_THRESHOLD, color='gray', linestyle=':', 
            label='Launch Threshold ({LAUNCH_ALTITUDE_THRESHOLD} m)')

# This 'if' statement checks if we actually found apogee.
if apogee_detected:
    # If we did, draw a horizontal red dashed ('--') line at the apogee altitude.
    ax1.axhline(y=apogee_alt, color='red', linestyle='--', 
                label=f'Apogee: {apogee_alt} m at {apogee_time}s')

# Set the main title for the entire graph.
plt.title('Simulated Flight Analysis (Altitude vs. Time)', fontsize=16)
# This tells the plot to show the legend (the box that explains what each line is).
ax1.legend(loc='upper right')
# This command automatically adjusts the plot to make sure labels aren't cut off.
plt.tight_layout()
# This command opens the plot window and displays the graph on our screen.
plt.show()

