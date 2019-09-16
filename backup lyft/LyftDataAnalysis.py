
# coding: utf-8

# # Import library
# run two cells below first

# In[2]:


import numpy as np
import pandas as pd
from collections import defaultdict
import time
from datetime import datetime
import sys
import math


# In[2]:


if 'holidays' not in sys.modules:
    get_ipython().system('pip install holidays')
import holidays


# # Load three csv files
# Summary: 937 unique drivers and 193502 unique rides in total

# In[2]:


driver_df = pd.read_csv('driver_ids.csv')
ride_df = pd.read_csv('ride_ids.csv')
ride_timestamps_df = pd.read_csv('ride_timestamps.csv')


# In[3]:


'''
Get the shape of each dataframe
'''
print('driver ids:',driver_df.shape)
display(driver_df.head())
print('ride ids:',ride_df.shape)
display(ride_df.head())
print('ride timestamps:',ride_timestamps_df.shape)
display(ride_timestamps_df.head())


# # Inspect Nan and abnormal values

# In[4]:


'''
Nan value inspection
'''
print('driver ids info:------------------------------')
driver_df.info()
print('ride ids info:--------------------------------')
ride_df.info()
print('ride timestamps info:-------------------------')
ride_timestamps_df.info()
'''
ride_timestamps has one Nan value in the column timestamp
    TODO: delete this ride or fill it with an artificial value?
'''
display(ride_timestamps_df[ride_timestamps_df.isnull().any(axis=1)])


# In[5]:


'''
Abnormal value inspection
'''
display(driver_df.describe())
display(ride_df.describe())
display(ride_timestamps_df.describe())


# In[6]:


'''
TODO: Need to think about how to deal with this case, why will ride_distance <= 0?
TODO: the number of ride_id in ride_df and that of ride_timestamps doesn't fit (193502 vs 194081)
'''
abnormal_ride_df = ride_df[ride_df.ride_distance <= 0]
print(abnormal_ride_df.shape)
display(abnormal_ride_df.head())


# In[7]:


'''
find overlap of driver_id between dirver_df and ride_df
TODO: some drivers don't have ride information--->delete? (937 vs 854)
'''
print(len(set(driver_df.driver_id.unique()).intersection(set(ride_df.driver_id.unique()))))


# In[8]:


'''
find overlap of ride_id between ride_df and ride_timestamps_df
TODO: some rides don't have ride timestamps--->delete? (193502 vs 184819)
'''
print(len(set(ride_df.ride_id.unique()).intersection(set(ride_timestamps_df.ride_id.unique()))))


# # Merge all dfs to one df

# In[9]:


'''
merge driver_df and ride_df (Get intersection based on driver_id)
'''
big_df = ride_df.merge(driver_df,left_on='driver_id',right_on='driver_id')
print(big_df.shape)
display(big_df.head())


# In[10]:


# get overlapped ride_id between big_df and ride_timestamps_df
big_df = big_df[big_df['ride_id'].isin(ride_timestamps_df.ride_id.unique())]
big_df.reset_index(drop=True,inplace=True)
print(big_df.shape)
display(big_df.head())


# In[11]:


start = time.time()
# for each unique ride id in big_df
for idx in range(big_df.shape[0]):
    rideid = big_df.iloc[idx]['ride_id']
    # first find rideid timestamps info in ride_timestamps_df
    target = ride_timestamps_df[ride_timestamps_df.ride_id == rideid]
    # for each (event,timestamp) pair
    for (e,t) in zip(list(target.event),list(target.timestamp)):
        big_df.at[idx,e] = t
    # double check index
    if big_df[big_df.ride_id == rideid]['requested_at'].values[0] !=     ride_timestamps_df[ride_timestamps_df.ride_id == rideid].iloc[0,-1]:
        print(idx)
print('duration:',(time.time()-start)/3600,'hrs')


# In[12]:


big_df.info()


# In[13]:


# saved for future use
big_df.to_csv('merged_big_driver_ride_df.csv',index=False)


# # Start to work on calculating extra variables
# If already have file 'merged_big_driver_ride_df.csv', directly start running code below

# In[26]:


def get_fare(driver_rides):
    total_fare = 0
    # if one single ride
    if driver_rides.ndim == 1:
        total_fare = (1 + driver_rides['ride_prime_time']/100)*(min(max(5,(2 + 1.15*driver_rides['ride_distance']                                                                            *0.00062 + 0.22                                                                            *driver_rides['ride_duration']/60                                                                             + 1.75)),400))
    else:
        for (distance,duration,prime) in zip(driver_rides['ride_distance'].values,                                             driver_rides['ride_duration'].values,                                             driver_rides['ride_prime_time'].values):
            total_fare += (1 + prime/100)*(min(max(5,(2 + 1.15*distance*0.00062 + 0.22*duration/60 + 1.75)),400))
    return total_fare


# In[27]:


merged_big_df = pd.read_csv('merged_big_driver_ride_df.csv')
print(merged_big_df.shape)
display(merged_big_df.head())


# In[19]:


# '''
# validate the correctness of combined df by randomly selecting ride ids to verify (random checking)
# '''
# ids = test1.ride_id
# i = np.random.choice(ids,10)
# for x in i:
#     display(test1[test1.ride_id == x])
#     display(ride_timestamps_df[ride_timestamps_df.ride_id == x])


# ## Get new variables related to ride info
# time of day: 0-6(midnight); 6-9(morning rush); 9-16(normal day); 16-19(evening rush); 19-24(fun) <br>
# season: {0: Spring, 1: Summer, 2: Autumn, 3: Winter}

# In[28]:


# variables related to ride
def add_vars(row):
    # convert time to datetime
    # source: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
    for i in range(5,len(row)):
        if type(row[i]) != float:
            row[i] = datetime.strptime(row[i], '%Y-%m-%d %H:%M:%S')
    # get speed
    row['speed(m/s)'] = row['ride_distance'] / row['ride_duration']
    # holiday? reference: https://stackoverflow.com/questions/2394235/detecting-a-us-holiday
    row['holiday'] = int(row['requested_at'] in holidays.US())
    # requested_at time is weekend? (0-6 --> Mon-Sun)
    row['weekend'] = int(row['requested_at'].weekday() > 4)
    # time of day (6-12/12-15/16-20/20-24/24-6)
    # {0: [6,9), 1: [9,16), 2: [16,19), 3: [19,24), 4: [0,6)}
    if 6 <= row['requested_at'].hour < 9:
        row['time of day'] = 0
    elif 9 <= row['requested_at'].hour < 16:
        row['time of day'] = 1
    elif 16 <= row['requested_at'].hour < 19:
        row['time of day'] = 2
    elif 19 <= row['requested_at'].hour < 24:
        row['time of day'] = 3
    else:
        row['time of day'] = 4
    # season (12-2 Winter/3-5 Spring/6-8 Summer/9-11 Autumn)
    # {0: Spring, 1: Summer, 2: Autumn, 3: Winter}
    if 3 <= row['requested_at'].month <= 5:
        row['season'] = 0
    elif 6 <= row['requested_at'].month <= 8:
        row['season'] = 1
    elif 9 <= row['requested_at'].month <= 11:
        row['season'] = 2
    else:
        row['season'] = 3
    # time spent from requested_at to arrived_at (efficiency of picking up a customer)
    if type(row['arrived_at']) != float:
        row['time spent to arrive at the customer(minutes)'] = (row['arrived_at']-                                                                row['requested_at']).total_seconds()/60
    else:
        row['time spent to arrive at the customer(minutes)'] = (row['picked_up_at']-                                                                row['requested_at']).total_seconds()/60
    # fare for this ride
    row['fare'] = get_fare(row)
    return row

start = time.time()
rides_added_vars_df = merged_big_df.apply(add_vars,axis=1)
print('duration:',(time.time() - start)/60,'minutes')


# In[29]:


print(rides_added_vars_df.shape)
display(rides_added_vars_df.head())


# In[30]:


# saved for future use
rides_added_vars_df.to_csv('added_variables_rides_info.csv',index=False)


# ## Get new variables related to drivers

# In[22]:


drivers_df = pd.DataFrame(rides_added_vars_df.driver_id.unique())
drivers_df.rename(columns={0:'driver_id'},inplace=True)
drivers_df.reset_index(drop=True,inplace=True)
print(drivers_df.shape)
display(drivers_df.head())


# In[24]:


def add_driver_vars(row):
    # first find all rides under driverid
    rides = rides_added_vars_df[rides_added_vars_df.driver_id == row['driver_id']]
    # Percentage of rides completed in prime time among all rides for each driver
    row['prime time rides percentage'] = rides[rides.ride_prime_time != 0].shape[0] / rides.shape[0]
    # Average active time per day for each driver (total duration / total days)
    sorted_days = rides.groupby('requested_at', as_index=False).mean()['requested_at']
    days = len(sorted_days.dt.normalize().unique())
    row['average daily active time(hrs/day)'] = rides.ride_duration.sum() / (3600*days)
    # Average fare(daily/per ride/monthly) received for each driver
    total_fare = get_fare(rides)
    row['gross fare(over all rides)'] = total_fare
    row['average daily fare'] = total_fare / days
    row['average fare per ride'] = total_fare / rides.shape[0]
    number_of_months = len(set([(x.year,x.month) for x in sorted_days]))
    row['average monthly fare'] = total_fare / number_of_months
    # Total number of rides
    row['total rides'] = rides.shape[0]
    # Number of abnormal rides (ride_distance <= 0)
    row['number of abnormal rides'] = rides[rides.ride_distance <= 0].shape[0]
    # Ride completion rate (1 - (# of abnormal / total rides))
    row['completion rate'] = 1 - (row['number of abnormal rides'] / row['total rides'])
    # Unique days of work
    row['active days'] = days
    # Average time spent on each ride (requested_at --> arrived_at) in minutes
    row['average arriving time(minutes)'] = rides['time spent to arrive at the customer(minutes)'].mean()
    return row

start = time.time()
drivers_added_vars_df = drivers_df.apply(add_driver_vars,axis=1)
print('duration:',(time.time() - start)/60,'minutes')


# In[25]:


print(drivers_added_vars_df.shape)
display(drivers_added_vars_df.head())


# In[26]:


# saved for future use
drivers_added_vars_df.to_csv('added_variables_drivers_info.csv',index=False)


# # Start to construct models

# In[27]:


'''
rides info combined dataframe
'''
big_rides_info = pd.read_csv('added_variables_rides_info.csv')
print(big_rides_info.shape)
display(big_rides_info.head())

'''
drivers info combined dataframe
'''
big_drivers_info = pd.read_csv('added_variables_drivers_info.csv')
print(big_drivers_info.shape)
display(big_drivers_info.head())

