# <b> Introduction </b>

These data come from a lab session done this semester in which students completed a baseline countermovement vertical jump (CMJ), <u> a 15-second Wingate test againts 7.5% of their body mass</u>, and then another CMJ. Goal of the lab was to introduce students to experimental designs by measuring somtehing prior to and after (CMJ perofrmance) some kind of intervention, in this case the intervention was the Wingate test. As well as introduce the energy systems

For their lab reports, students were given some discrete variables all calculated via the Hawkin force plates such as:
<ul>
    <li> <i> Jump height (cm) via impulse-momentum. </i>
    <li> <i> Modified reactive strength index (AU). </i>
</ul>

For my own purposes of learning and improving my skills as a Python coder, I choose to use [the spm1d package](https://spm1d.org/index.html) for Statistical Parameteric Mapping (SPM) of the CMJ force time curves prior to and after the Wingate. This is a package I have been wanting to experiment with for a while. Since in exercise and sports science, we spend so much time on discrete (peaks, means, etc.) variables but collect much more data than we actually analyze. SPM allows for the analysis of the entire force-time curve. 


```python
# import packages
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from tkinter.filedialog import askdirectory
import spm1d
from IPython.display import display, Markdown

# defining plot theme. 
custom_theme = {"axes.spines.right": False, "axes.spines.top": False,
                "axes.titlelocation": "center", "axes.titley": 1,
                "font.weight":"bold", "axes.titlesize": "x-large", "axes.labelsize": "x-large",
                "axes.titleweight": "bold", "axes.labelweight": 'bold'}

plt.rcParams.update({**custom_theme})
```

## <b> Data Loading </b>
Select the directory where the files are stored (clone the git repo if necessary). Print the file names and check the number of files that will be analyzed. 


```python
dir_to_read = askdirectory(title = 'Select Directory to Read CMJ Files')
files_to_read = os.listdir(dir_to_read)

for file_to_print in files_to_read:
    print(file_to_print[:-4])
print(f'\nThere are {len(files_to_read)} files.')
```

    001-POST
    001-PRE
    002-POST
    002-PRE
    003-POST
    003-PRE
    004-POST
    004-PRE
    005-POST
    005-PRE
    006-POST
    006-PRE
    007-POST
    007-PRE
    008-POST
    008-PRE
    009-POST
    009-PRE
    
    There are 18 files.
    

## <b> Custom Function for Analyzing CMJ Force Time Arrays
Next, I'm writing a custom function to read the force arrays, identify the indices we need, crop the arrays to those indices, and then interpolate the data to 101 data points (0-100% of the CMJ phase of interest).</b>

Specifically, the CMJ force time data will be cropped from the point of movement initation ('start_move') to takeoff ('takeoff').

The index identification portion of the below code has been adapted from [Merrigan et al.](https://journals.lww.com/nsca-jscr/fulltext/2022/09000/analyzing_force_time_curves__comparison_of.4.aspx). 



```python
# This is a custom function to read, analyze (find the indices of interest), crop, and interpolate the CMJ data
sf = 1000 # Hawkin sampling frequency = 1000 Hz

def read_and_crop_and_interpolate_cmj(file_path):
    full_data = pd.read_csv(file_path)
    fz_total = full_data.iloc[:,0] # data are stored in the first column from how I set it up to export from R's {HawkinR} package.     
    
    # calculate baseline fz ('weighing phase') - mean of first 1-second of data.
    bw_mean = fz_total[0:1000].mean()
    
    # calculate baseline standard deviation for determination of movement start.
    bw_sd = fz_total[0:1000].std()
    
    # convert body weight in Newtons to body mass in kilograms. 
    bodymass = bw_mean/9.81

    # this determines when movement begins
    start_move = 20 # temporarily assign the start move index to the 20th index of the array
    
    # while loop to identify the point at which the fz_total array deviates from the mean by 5 standard deviations
    while fz_total[start_move] > (bw_mean - (bw_sd * 5)):
        start_move = start_move + 1

    # backtrack start_move to within 1 standard deviation of the baseline force
    while fz_total[start_move] < (bw_mean - bw_sd):
        start_move = start_move -1
    
    # identify takeoff index of original dataframe as when force drops below 30 N    
    takeoff = start_move # first say that takeoff index = start_move index
    while fz_total[takeoff] > 30:
        takeoff = takeoff + 1
        
    # crop the array from start movement to takeoff
    cropped_fz_total_original = fz_total[start_move:takeoff]
    
    # normalize to bodymass in kilos so N/kg is comparable between subjects
    cropped_fz_normalized = cropped_fz_total_original/bodymass
    
    # interpolate to 101 datapoints
    original_data = np.linspace(0, len(cropped_fz_normalized)-1, len(cropped_fz_normalized))
    interpolated_indices = np.linspace(0, len(cropped_fz_normalized)-1, 101)
    force_interpolated = np.interp(interpolated_indices, original_data, cropped_fz_normalized)
    
    # return the cropped, normalized and interpolated array
    return(force_interpolated)
```

<b> We just wrote that custom function, now apply it in a for loop over the files we need to read, crop, normalize, and interpolate. </b>

For sanity's check as well, we will be creating a Spaghetti plot of all the arrays in the loop.


```python
# preallocate a panda's dataframe to store the data in
data_to_save = pd.DataFrame()

# initalize a plot
plt.figure(figsize = (10, 8))

# for loop
for file_name in files_to_read:
    file_path_of_choice = os.path.join(dir_to_read, file_name) # get the full file path by joining the directory we selected with the filename
    
    # apply the function
    cleaned_and_interpolated_data = read_and_crop_and_interpolate_cmj(file_path=file_path_of_choice)
    
    # remove the .csv from the filename
    base_file_name = file_name[:-4]
    
    # append the dataframe with the values we just generated...
    data_to_save[base_file_name] = cleaned_and_interpolated_data
    
    # plot the data for sanity checks. always. 
    plt.plot(cleaned_and_interpolated_data, label = base_file_name)

# outside of the loop, figure theme settings
plt.legend(loc = 'upper left', frameon = False, ncol = 2)
plt.ylabel('Force (N/kg)')
plt.xlabel('Time (0-100%)');
```


    
![png](output_files/output_7_0.png)
    


<b> Things look good! All CMJs have been cropped, interpolated, and normalized correctly. Let's check the dataframe now. </b>


```python
display(Markdown(data_to_save.head(10).to_markdown(index = False))) 
```


|   001-POST |   001-PRE |   002-POST |   002-PRE |   003-POST |   003-PRE |   004-POST |   004-PRE |   005-POST |   005-PRE |   006-POST |   006-PRE |   007-POST |   007-PRE |   008-POST |   008-PRE |   009-POST |   009-PRE |
|-----------:|----------:|-----------:|----------:|-----------:|----------:|-----------:|----------:|-----------:|----------:|-----------:|----------:|-----------:|----------:|-----------:|----------:|-----------:|----------:|
|    9.77584 |   9.77923 |    9.80693 |   9.7971  |    9.7665  |   9.7746  |    9.76429 |   9.78211 |    9.78569 |   9.79626 |    9.78405 |   9.81209 |    9.77762 |   9.76969 |    9.77608 |   9.76998 |    9.7876  |   9.79097 |
|    9.72328 |   9.63245 |    9.71184 |   9.57312 |    9.5863  |   9.65132 |    9.7137  |   9.70618 |    9.63817 |   9.73073 |    9.56899 |   9.6806  |    9.59948 |   9.54299 |    9.57811 |   9.61833 |    9.70896 |   9.74085 |
|    9.65495 |   9.50317 |    9.59261 |   9.28473 |    9.38781 |   9.57101 |    9.65223 |   9.65607 |    9.51523 |   9.60819 |    9.32111 |   9.51362 |    9.39245 |   9.30519 |    9.26496 |   9.47444 |    9.70394 |   9.67468 |
|    9.6532  |   9.37389 |    9.47904 |   8.93162 |    9.15834 |   9.45759 |    9.46605 |   9.62949 |    9.37591 |   9.41358 |    9.17665 |   9.35813 |    9.16028 |   8.9905  |    8.89422 |   9.32667 |    9.70394 |   9.64795 |
|    9.67422 |   9.23481 |    9.33357 |   8.56777 |    8.84933 |   9.40475 |    9.2528  |   9.6176  |    9.26117 |   9.24845 |    9.24888 |   9.16847 |    8.92811 |   8.70196 |    8.30751 |   9.12249 |    9.71063 |   9.58914 |
|    9.70138 |   9.08034 |    9.07812 |   8.15978 |    8.44318 |   9.29908 |    9.06043 |   9.60494 |    9.15052 |   9.02959 |    9.51318 |   8.9788  |    8.50495 |   8.30721 |    7.58042 |   8.94479 |    9.77087 |   9.52364 |
|    9.67072 |   8.95105 |    8.8319  |   7.73688 |    8.02226 |   9.21666 |    8.90954 |   9.6176  |    9.03169 |   8.85529 |    9.77748 |   8.68657 |    8.05288 |   8.01313 |    6.68056 |   8.74493 |    9.77087 |   9.47151 |
|    9.6532  |   8.90452 |    8.54768 |   7.33455 |    7.56191 |   9.11486 |    8.6887  |   9.58318 |    8.88416 |   8.67116 |    9.72331 |   8.36378 |    7.63565 |   7.72777 |    5.67272 |   8.53255 |    9.7374  |   9.44611 |
|    9.61115 |   8.76457 |    8.30876 |   6.94655 |    7.17688 |   8.98206 |    8.3381  |   9.4784  |    8.68746 |   8.50407 |    9.42946 |   8.00482 |    7.40566 |   7.55496 |    4.67927 |   8.3242  |    9.68721 |   9.35388 |
|    9.47888 |   8.72066 |    8.06001 |   6.58747 |    6.801   |   8.82356 |    7.89428 |   9.41968 |    8.46618 |   8.36843 |    8.91891 |   7.56731 |    7.2103  |   7.39167 |    3.8442  |   8.08851 |    9.63116 |   9.2396  |


<b> Check the shape of the dataframe we created. We should have 18 columns (9 subjects, 2 conditions = 18) and 101 rows (101 datapoints).


```python
print(f'There are {data_to_save.shape[1]} columns. And there are {data_to_save.shape[0]} rows.')
```

    There are 18 columns. And there are 101 rows.
    

# <b> Data Cleaning </b>
<b> The next chunk will create the two arrays we will be analyzing in spm1d at - PRE vs. POST.</b>

<ol>
<li> First, filter the dataframes into post_df and pre_df based on column names
<li> Then transpose the dataframes into a J x Q matrix (subjects [rows] X nodes/points per trial [columns])
<li> Lastly, transfer the dataframe into an array for ease. 



```python
post_df = data_to_save.loc[:, data_to_save.columns.str.contains('POST')]
pre_df = data_to_save.loc[:, data_to_save.columns.str.contains('PRE')]

post_transpose = post_df.T
pre_transpose = pre_df.T

pre_ft = np.array(pre_transpose)
post_ft = np.array(post_transpose)
```

<b> Going to arrange the data so we can plot it as mean +/- SD for PRE and POST in the next code block. 


```python
pre_mean = pre_ft.mean(axis = 0)
pre_sd = pre_ft.std(axis = 0)

post_mean = post_ft.mean(axis = 0)
post_sd = post_ft.std(axis = 0)

# make an x values
x_vals = np.arange(101)

# plot mean and SD for fun
plt.figure(figsize = (14, 6))

# plt.subplot reminder plt.subplot(rows, columns, plot index)
plt.subplot(1, 2, 1)
plt.plot(x_vals, pre_mean, color = 'blue', linewidth = 4)
plt.fill_between(x_vals, pre_mean - pre_sd, pre_mean + pre_sd, color = 'blue', alpha = 0.1)
plt.xlim(0, 100)
plt.ylim(0, 30)
plt.ylabel('Force (N/kg)')
plt.title('PRE')

# plot the post data
# plt.subplot reminder plt.subplot(rows, columns, plot index)
plt.subplot(1, 2, 2)
plt.plot(x_vals, post_mean, color = 'red', linewidth = 4)
plt.fill_between(x_vals, post_mean - post_sd, post_mean + post_sd, color = 'red', alpha = 0.1)
plt.xlim(0, 100)
plt.ylim(0, 30)
plt.title('POST')
plt.tight_layout()
```


    
![png](output_files/output_15_0.png)
    


# <b> Running the SPM1D analysis. </b>
Now, this next code block will run the spm1d analyses.


```python
t = spm1d.stats.ttest_paired(pre_ft, post_ft)
t
```




    SPM{t}
       SPM.z      :  (1x101) test stat field
       SPM.df     :  (1, 8)
       SPM.fwhm   :  4.15726
       SPM.resels :  (1, 24.05429)
    
    



<b> Return the inferential stats of the SPM.


```python
alpha = 0.05
ti = t.inference(alpha = alpha)
ti
```




    SPM{t} inference field
       SPM.z         :  (1x101) raw test stat field
       SPM.df        :  (1, 8)
       SPM.fwhm      :  4.15726
       SPM.resels    :  (1, 24.05429)
    Inference:
       SPM.alpha     :  0.050
       SPM.zstar     :  5.56250
       SPM.h0reject  :  False
       SPM.p_set     :  1.000
       SPM.p_cluster :  ()
    
    




```python
plt.figure(figsize = (10,8))
ti.plot()
ti.plot_threshold_label()
plt.xlabel('Time (0-100%)');
```


    
![png](output_files/output_20_0.png)
    


# <b> Conclusion </b>
From the results of the SPM analysis, there was no effect of the 15-second Wingate test on CMJ performance. 
