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
    


<b> Things look good! Let's check the dataframe now.


```python
data_to_save.head(10)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>001-POST</th>
      <th>001-PRE</th>
      <th>002-POST</th>
      <th>002-PRE</th>
      <th>003-POST</th>
      <th>003-PRE</th>
      <th>004-POST</th>
      <th>004-PRE</th>
      <th>005-POST</th>
      <th>005-PRE</th>
      <th>006-POST</th>
      <th>006-PRE</th>
      <th>007-POST</th>
      <th>007-PRE</th>
      <th>008-POST</th>
      <th>008-PRE</th>
      <th>009-POST</th>
      <th>009-PRE</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>9.775837</td>
      <td>9.779228</td>
      <td>9.806930</td>
      <td>9.797101</td>
      <td>9.766499</td>
      <td>9.774600</td>
      <td>9.764290</td>
      <td>9.782109</td>
      <td>9.785691</td>
      <td>9.796256</td>
      <td>9.784046</td>
      <td>9.812087</td>
      <td>9.777619</td>
      <td>9.769693</td>
      <td>9.776079</td>
      <td>9.769985</td>
      <td>9.787597</td>
      <td>9.790969</td>
    </tr>
    <tr>
      <th>1</th>
      <td>9.723279</td>
      <td>9.632452</td>
      <td>9.711841</td>
      <td>9.573125</td>
      <td>9.586303</td>
      <td>9.651317</td>
      <td>9.713698</td>
      <td>9.706181</td>
      <td>9.638169</td>
      <td>9.730729</td>
      <td>9.568994</td>
      <td>9.680602</td>
      <td>9.599484</td>
      <td>9.542988</td>
      <td>9.578110</td>
      <td>9.618327</td>
      <td>9.708962</td>
      <td>9.740845</td>
    </tr>
    <tr>
      <th>2</th>
      <td>9.654953</td>
      <td>9.503170</td>
      <td>9.592608</td>
      <td>9.284729</td>
      <td>9.387806</td>
      <td>9.571007</td>
      <td>9.652228</td>
      <td>9.656068</td>
      <td>9.515233</td>
      <td>9.608194</td>
      <td>9.321110</td>
      <td>9.513616</td>
      <td>9.392452</td>
      <td>9.305186</td>
      <td>9.264958</td>
      <td>9.474439</td>
      <td>9.703943</td>
      <td>9.674681</td>
    </tr>
    <tr>
      <th>3</th>
      <td>9.653201</td>
      <td>9.373888</td>
      <td>9.479038</td>
      <td>8.931616</td>
      <td>9.158337</td>
      <td>9.457586</td>
      <td>9.466049</td>
      <td>9.629493</td>
      <td>9.375905</td>
      <td>9.413579</td>
      <td>9.176647</td>
      <td>9.358134</td>
      <td>9.160283</td>
      <td>8.990495</td>
      <td>8.894216</td>
      <td>9.326666</td>
      <td>9.703943</td>
      <td>9.647948</td>
    </tr>
    <tr>
      <th>4</th>
      <td>9.674224</td>
      <td>9.234810</td>
      <td>9.333574</td>
      <td>8.567766</td>
      <td>8.849328</td>
      <td>9.404750</td>
      <td>9.252803</td>
      <td>9.617597</td>
      <td>9.261165</td>
      <td>9.248452</td>
      <td>9.248878</td>
      <td>9.168467</td>
      <td>8.928114</td>
      <td>8.701962</td>
      <td>8.307507</td>
      <td>9.122489</td>
      <td>9.710635</td>
      <td>9.589135</td>
    </tr>
    <tr>
      <th>5</th>
      <td>9.701380</td>
      <td>9.080337</td>
      <td>9.078117</td>
      <td>8.159777</td>
      <td>8.443183</td>
      <td>9.299079</td>
      <td>9.060426</td>
      <td>9.604943</td>
      <td>9.150523</td>
      <td>9.029592</td>
      <td>9.513179</td>
      <td>8.978800</td>
      <td>8.504945</td>
      <td>8.307211</td>
      <td>7.580421</td>
      <td>8.944788</td>
      <td>9.770866</td>
      <td>9.523639</td>
    </tr>
    <tr>
      <th>6</th>
      <td>9.670721</td>
      <td>8.951055</td>
      <td>8.831900</td>
      <td>7.736877</td>
      <td>8.022255</td>
      <td>9.216655</td>
      <td>8.909535</td>
      <td>9.617597</td>
      <td>9.031685</td>
      <td>8.855291</td>
      <td>9.777480</td>
      <td>8.686574</td>
      <td>8.052879</td>
      <td>8.013130</td>
      <td>6.680561</td>
      <td>8.744928</td>
      <td>9.770866</td>
      <td>9.471510</td>
    </tr>
    <tr>
      <th>7</th>
      <td>9.653201</td>
      <td>8.904520</td>
      <td>8.547678</td>
      <td>7.334554</td>
      <td>7.561910</td>
      <td>9.114859</td>
      <td>8.688700</td>
      <td>9.583177</td>
      <td>8.884162</td>
      <td>8.671161</td>
      <td>9.723306</td>
      <td>8.363777</td>
      <td>7.635648</td>
      <td>7.727767</td>
      <td>5.672717</td>
      <td>8.532549</td>
      <td>9.737404</td>
      <td>9.446113</td>
    </tr>
    <tr>
      <th>8</th>
      <td>9.611155</td>
      <td>8.764567</td>
      <td>8.308765</td>
      <td>6.946547</td>
      <td>7.176881</td>
      <td>8.982065</td>
      <td>8.338097</td>
      <td>9.478395</td>
      <td>8.687465</td>
      <td>8.504067</td>
      <td>9.429456</td>
      <td>8.004822</td>
      <td>7.405656</td>
      <td>7.554965</td>
      <td>4.679272</td>
      <td>8.324200</td>
      <td>9.687212</td>
      <td>9.353885</td>
    </tr>
    <tr>
      <th>9</th>
      <td>9.478883</td>
      <td>8.720657</td>
      <td>8.060014</td>
      <td>6.587469</td>
      <td>6.801003</td>
      <td>8.823558</td>
      <td>7.894277</td>
      <td>9.419677</td>
      <td>8.466180</td>
      <td>8.368427</td>
      <td>8.918913</td>
      <td>7.567305</td>
      <td>7.210301</td>
      <td>7.391674</td>
      <td>3.844202</td>
      <td>8.088511</td>
      <td>9.631163</td>
      <td>9.239601</td>
    </tr>
  </tbody>
</table>
</div>



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
    

